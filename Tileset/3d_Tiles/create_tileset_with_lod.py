import math
import json

# Quadrant remapping: 1→2, 2→4, 3→1, 4→3
QUADRANT_MAP = {1: 2, 2: 4, 3: 1, 4: 3}

# Geographic bounds (degrees)
minLat, maxLat = 34.07201, 34.21606
minLon, maxLon = 77.45396, 77.62802

# Height bounds
minHeight = 3162.0
maxHeight = 4685.0

def calculate_udim(row, col):
    # Original quadrant detection
    if row < 8 and col < 8:
        quadrant = 1
    elif row < 8 and col >= 8:
        quadrant = 2
    elif row >= 8 and col < 8:
        quadrant = 3
    else:
        quadrant = 4

    # Get remapped quadrant
    new_quadrant = QUADRANT_MAP[quadrant]
    
    # Calculate local coordinates within original quadrant
    local_i = row % 8
    local_j = col % 8
    
    # Transform coordinates for 90° CCW rotation
    if new_quadrant == 2:  # Former quadrant 1
        udim_i = 7 - local_j  # Flip Y axis
        udim_j = local_i
    elif new_quadrant == 4:  # Former quadrant 2
        udim_i = 7 - local_j
        udim_j = local_i
    elif new_quadrant == 1:  # Former quadrant 3
        udim_i = 7 - local_j
        udim_j = local_i
    else:  # new_quadrant == 3 (former 4)
        udim_i = 7 - local_j
        udim_j = local_i

    return f"{new_quadrant}_{1001 + udim_i * 10 + udim_j}"


def compute_child_regions(minLat, maxLat, minLon, maxLon, num_rows, num_cols):
    lat_step = (maxLat - minLat) / num_rows
    lon_step = (maxLon - minLon) / num_cols

    regions = []
    for row in range(num_rows):
        for col in range(num_cols):
            # Calculate tile bounds in degrees
            tile_minLat = minLat + row * lat_step
            tile_maxLat = tile_minLat + lat_step
            tile_minLon = minLon + col * lon_step
            tile_maxLon = tile_minLon + lon_step

            # Convert to radians for Cesium's region
            west = math.radians(tile_minLon)
            south = math.radians(tile_minLat)
            east = math.radians(tile_maxLon)
            north = math.radians(tile_maxLat)

            regions.append([west, south, east, north, minHeight, maxHeight])
    return regions


# Initialize tileset with root
tileset = {
    "asset": {"version": "1.0", "gltfUpAxis": "Y"},
    "geometricError": 1000,
    "root": {
        "transform": [
            -0.976450790243208, 0.21574024713393025, 0, 0,
            -0.12108991487890734, -0.5480588098176702, 0.8276284030262898, 0,
            0.17855275620395158, 0.808138408162744, 0.5612764261076174, 0,
            1140597.9510803188, 5162401.478064311, 3561440.7474683644, 1
        ],
        "boundingVolume": {
            "region": [
                math.radians(minLon), math.radians(minLat),
                math.radians(maxLon), math.radians(maxLat),
                minHeight, maxHeight
            ]
        },
        "geometricError": 800,
        "refine": "ADD",
        "children": []
    }
}

# Generate HLOD levels
def build_hierarchy():
    # Level 4: Leaf nodes (16x16 = 256 tiles)
    level4_regions = compute_child_regions(minLat, maxLat, minLon, maxLon, 16, 16)
    level4_tiles = []
    for i, region in enumerate(level4_regions):
        row = i // 16
        col = i % 16
        udim = calculate_udim(row, col)
        level4_tiles.append({
            "boundingVolume": {"region": region},
            "geometricError": 50,
            "content": {"uri": f"{udim}_.glb"},
            "metadata": {"original_row": row, "original_col": col}
        })

    # Level 3: 8x8 tiles (parents of 4x4 level4 tiles)
    level3_regions = compute_child_regions(minLat, maxLat, minLon, maxLon, 8, 8)
    level3_tiles = []
    for i, region in enumerate(level3_regions):
        row3 = i // 8
        col3 = i % 8
        children = []
        for dr in [0, 1]:
            for dc in [0, 1]:
                child_idx = (row3 * 2 + dr) * 16 + (col3 * 2 + dc)
                children.append(level4_tiles[child_idx])
        level3_tiles.append({
            "boundingVolume": {"region": region},
            "geometricError": 100,
            "children": children
        })

    # Level 2: 4x4 tiles (parents of level3 tiles)
    level2_regions = compute_child_regions(minLat, maxLat, minLon, maxLon, 4, 4)
    level2_tiles = []
    for i, region in enumerate(level2_regions):
        row2 = i // 4
        col2 = i % 4
        children = []
        for dr in [0, 1]:
            for dc in [0, 1]:
                child_idx = (row2 * 2 + dr) * 8 + (col2 * 2 + dc)
                children.append(level3_tiles[child_idx])
        level2_tiles.append({
            "boundingVolume": {"region": region},
            "geometricError": 200,
            "children": children
        })

    # Level 1: 2x2 tiles (parents of level2 tiles)
    level1_regions = compute_child_regions(minLat, maxLat, minLon, maxLon, 2, 2)
    level1_tiles = []
    for i, region in enumerate(level1_regions):
        row1 = i // 2
        col1 = i % 2
        children = []
        for dr in [0, 1]:
            for dc in [0, 1]:
                child_idx = (row1 * 2 + dr) * 4 + (col1 * 2 + dc)
                children.append(level2_tiles[child_idx])
        level1_tiles.append({
            "boundingVolume": {"region": region},
            "geometricError": 400,
            "children": children
        })

    # Attach level1 tiles to root
    tileset["root"]["children"] = level1_tiles

build_hierarchy()

# Save to JSON
with open("tileset-all.json", "w") as f:
    json.dump(tileset, f, indent=4)