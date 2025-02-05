import bpy
import os
import json
from mathutils import Vector

# Configuration
EXPORT_PATH = r"C:\Users\THREE\Desktop\Blosm\3dtiles"
TILE_BASE_NAME = "Terrain"
MAIN_TILESET_JSON = os.path.join(EXPORT_PATH, "tileset.json")

# World parameters
QUADRANTS = {
    1: {"x_range": (-7999.99951171875, 0), "y_range": (-8000.00048828125, 0)},
    2: {"x_range": (-8000.0, 0), "y_range": (0, 8000.0)},
    3: {"x_range": (0, 8000.0), "y_range": (-8000.0, 0)},
    4: {"x_range": (0, 8000.0), "y_range": (0, 8000.0)}
}
x_segments = 16
y_segments = 16
x_step = (8000.0 - -7999.99951171875) / x_segments  # 1000 units per tile
y_step = (8000.0 - -8000.00048828125) / y_segments

TILE_SIZE = x_step
WORLD_SIZE = 16000  # (-8000 to 8000 in both axes)
QUADRANT_SIZE = WORLD_SIZE // 2
TILE_COUNT = 8  # 8x8 tiles per quadrant
TILE_SIZE = QUADRANT_SIZE // TILE_COUNT

temp_cols = []
# Create temporary collections
for q, ranges in QUADRANTS.items():
    col = bpy.data.collections.new(f"Temp_Merge_Q{q}")
    temp_cols.append(col)
    bpy.context.scene.collection.children.link(col)
def get_quadrant_and_udim(obj):
    """Calculate quadrant and UDIM index from object location"""
    bb_world = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    center = sum(bb_world, Vector()) / len(bb_world)
    
    # Determine quadrant
    for q, ranges in QUADRANTS.items():
        if (ranges["x_range"][0] <= center.x <= ranges["x_range"][1] and
            ranges["y_range"][0] <= center.y <= ranges["y_range"][1]):
            
            local_x = center.x - ranges["x_range"][0]
            local_y = center.y - ranges["y_range"][0]
            udim_x = int(local_x // TILE_SIZE)
            udim_y = int(local_y // TILE_SIZE)
            
            udim = 1001 + (udim_y * 10) + udim_x
            
            return q, udim
    
    return None, None

def merge_tile_group(group, quadrant):
    """Merge 4 tiles and store metadata in custom properties"""
    col = temp_cols[quadrant -1]
    
    # Copy and join objects
    copies = []
    for obj in group:
        copy = obj.copy()
        copy.data = obj.data.copy()
        col.objects.link(copy)
        copies.append(copy)
    
    bpy.ops.object.select_all(action='DESELECT')
    for copy in copies:
        copy.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    
    merged_obj = bpy.context.active_object
    merged_obj.name = f"{TILE_BASE_NAME}_Q{quadrant}_L1_{merged_obj.name.split('_')[-1]}"
    
    # Apply transforms and weld
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Store metadata
    child_names = [obj.name for obj in group]
    merged_obj["child_tiles"] = ",".join(child_names)
    merged_obj["quadrant"] = quadrant
    merged_obj["lod_level"] = 1
    
    
    return merged_obj

def export_quadrant(quadrant):
    """Export quadrant to separate blend file with custom properties"""
    quadrant_objects = [obj for obj in bpy.data.objects 
                       if obj.get("quadrant") == quadrant]
    
    # Create dedicated collection
    quadrant_col = bpy.data.collections.new(f"Quadrant_{quadrant}")
    bpy.context.scene.collection.children.link(quadrant_col)
    
    # Add objects to collection
    for obj in quadrant_objects:
        try:
            quadrant_col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        except:
            pass
    
    # Save blend file
    quadrant_path = os.path.join(EXPORT_PATH, f"quadrant_{quadrant}.blend")
    bpy.data.libraries.write(quadrant_path, {quadrant_col}, fake_user=True)
    
    # Cleanup
    bpy.data.collections.remove(quadrant_col)
    return len(quadrant_objects)

def generate_tileset_json():
    """Generate main 3D Tiles JSON referencing quadrant files"""
    tileset = {
        "asset": {"version": "1.0"},
        "geometricError": WORLD_SIZE,
        "root": {
            "boundingVolume": {
                "region": [
                    -1.319700, 0.698858,  # WGS84 bounds (example)
                    -1.319400, 0.699200,
                    0, 1500
                ]
            },
            "geometricError": WORLD_SIZE/2,
            "refine": "ADD",
            "children": []
        }
    }
    
    # Add quadrants as root children
    for q in [1, 2, 3, 4]:
        quadrant_entry = {
            "boundingVolume": calculate_quadrant_volume(q),
            "geometricError": QUADRANT_SIZE,
            "content": {
                "uri": f"quadrant_{q}.blend",
                "type": "blend"
            },
            "children": []
        }
        tileset["root"]["children"].append(quadrant_entry)
    
    # Save tileset
    with open(MAIN_TILESET_JSON, 'w') as f:
        json.dump(tileset, f, indent=2)

def calculate_quadrant_volume(quadrant):
    """Calculate bounding region for quadrant in WGS84"""
    # Example coordinates - replace with your actual geo-bounds
    west = -1.319700 + (0.0001 * (quadrant-1) % 2)
    south = 0.698858 + (0.0001 * (quadrant-1) // 2)
    return {
        "region": [
            west, south,
            west + 0.0002, south + 0.0002,
            0, 1500
        ]
    }

def process_all_quadrants():
    """Main processing function"""
    # Process all tiles
    all_tiles = [obj for obj in bpy.data.objects]
    
    # Organize by quadrant
    quadrant_map = {1: [], 2: [], 3: [], 4: []}
    for tile in all_tiles:
        quadrant, udim = get_quadrant_and_udim(tile)
        tile.name = f"{TILE_BASE_NAME}_Q{quadrant}_{udim}"
        tile["quadrant"] = quadrant
        tile["udim"] = udim
        tile["lod_level"] = 0
        quadrant_map[quadrant].append(tile)
    
    # Process each quadrant
    for quadrant in [1, 2, 3, 4]:
        # Merge tiles into 4x4 groups (LOD 1)
        tiles = quadrant_map[quadrant]
        for i in range(0, TILE_COUNT, 2):
            for j in range(0, TILE_COUNT, 2):
                # Get 2x2 tile group
                group = [t for t in tiles 
                        if (i <= (t["udim"] - 1001) % 10 < i+2) and
                           (j <= (t["udim"] - 1001) // 10 < j+2)]
                
                if len(group) == 4:
                    merge_tile_group(group, quadrant)
        
        # Export quadrant
        count = export_quadrant(quadrant)
        print(f"Exported quadrant {quadrant} with {count} objects")
    
    # Generate main tileset
    generate_tileset_json()
    # Cleanup temporary collection
    # for q, ranges in QUADRANTS.items():
    #     bpy.data.collections.remove(temp_cols[q - 1])

    print(f"Generated main tileset at {MAIN_TILESET_JSON}")

# Run the processing
process_all_quadrants()