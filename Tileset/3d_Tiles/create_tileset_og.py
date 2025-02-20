import math

# Quadrant remapping: 1→2, 2→4, 3→1, 4→3
QUADRANT_MAP = {1: 2, 2: 4, 3: 1, 4: 3}

# Geographic bounds (degrees)
minLat, maxLat = 34.07201, 34.21606
minLon, maxLon = 77.45396, 77.62802

# Split into 16x16 grid (256 tiles)
num_rows = 16
num_cols = 16

# Height bounds (from your terrain_bbox)
minHeight = 3162.0
maxHeight = 4685.0
tileset = {
    "asset": {
        "version": "1.0",
        "gltfUpAxis": "Y"
    },
    "geometricError": 1000,
    "root": {
        "transform": [
            -0.976450790243208,
            0.21574024713393025,
            0,
            0,
            -0.12108991487890734,
            -0.5480588098176702,
            0.8276284030262898,
            0,
            0.17855275620395158,
            0.808138408162744,
            0.5612764261076174,
            0,
            1140597.9510803188,
            5162401.478064311,
            3561440.7474683644,
            1
        ],
        "boundingVolume": {
            "region": [
                math.radians(minLon),
                math.radians(minLat),
                math.radians(maxLon),
                math.radians(maxLat),
                minHeight,
                maxHeight
            ]
        },
        "geometricError": 500,
        "refine": "ADD",
        "children": []
    }
}


# def compute_child_regions(minLat, maxLat, minLon, maxLon, num_rows, num_cols):
#     lat_step = (maxLat - minLat) / num_rows
#     lon_step = (maxLon - minLon) / num_cols

#     regions = []
#     for row in range(num_rows):
#         for col in range(num_cols):
#             # Calculate tile bounds in degrees
#             tile_minLat = minLat + row * lat_step
#             tile_maxLat = minLat + (row + 1) * lat_step
#             tile_minLon = minLon + col * lon_step
#             tile_maxLon = minLon + (col + 1) * lon_step

#             # Convert to radians for Cesium's region
#             west = math.radians(tile_minLon)
#             south = math.radians(tile_minLat)
#             east = math.radians(tile_maxLon)
#             north = math.radians(tile_maxLat)
#             regions.append([west, south, east, north, minHeight, maxHeight])
#     return regions

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

child_regions = compute_child_regions(minLat, maxLat, minLon, maxLon, num_rows, num_cols)
# Add child tiles (replace "tile_{row}_{col}.glb" with your GLB filenames)
# Generate tileset with corrected mapping
for i, region in enumerate(child_regions):
    row = i // num_cols
    col = i % num_cols
    
    # Get properly rotated UDIM
    udim = calculate_udim(row, col)
    
    tileset["root"]["children"].append({
        "boundingVolume": {"region": region},
        "geometricError": 200,
        "content": {"uri": f"{udim}.glb"},
        "metadata": {"original_row": row, "original_col": col}
    })
# Save to JSON
import json
with open("tileset.json", "w") as f:
    json.dump(tileset, f, indent=4)
    