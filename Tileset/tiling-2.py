import bpy
import os
import json
import bmesh
from mathutils import Vector

# Configuration
EXPORT_PATH = r"C:\Users\THREE\Desktop\Blosm\3dtiles"  # Blender relative export path
TILE_BASE_NAME = "Terrain"
JSON_PATH = r"C:\Users\THREE\Desktop\Blosm"

# Terrain grid parameters (adjusted for 8x8 grid -> 64 tiles)
x_min = -7999.99951171875
x_max = 8000.0
y_min = -8000.00048828125
y_max = 8000.0
x_segments = 16
y_segments = 16
x_step = (x_max - x_min) / x_segments  # 1000 units per tile
y_step = (y_max - y_min) / y_segments

def get_tile_coordinates(obj):
    """Calculate original grid coordinates from object's bounding box"""
    bbox_corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    center = sum(bbox_corners, Vector()) / len(bbox_corners)
    i = int((center.x - x_min) // x_step)
    j = int((center.y - y_min) // y_step)
    return max(0, min(i, x_segments-1)), max(0, min(j, y_segments-1))

def merge_tile_group(group_objects, parent_i, parent_j):
    """Merge 4 tiles into a single mesh with vertex welding"""
    bm = bmesh.new()
    
    # Collect geometry from all tiles
    for obj in group_objects:
        temp_bm = bmesh.new()
        temp_bm.from_mesh(obj.data)
        temp_bm.transform(obj.matrix_world)
        bm.from_mesh(obj.data)
        temp_bm.free()
    
    # Weld vertices and clean up
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
    
    # Create new object
    me = bpy.data.meshes.new(f"{TILE_BASE_NAME}_L1_{parent_i}_{parent_j}")
    bm.to_mesh(me)
    ob = bpy.data.objects.new(me.name, me)
    bpy.context.collection.objects.link(ob)
    return ob

def calculate_bounding_volume(obj):
    """Calculate 3D Tiles bounding box in WGS84 (simplified example)"""
    local_bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    min_point = Vector((min(v.x for v in local_bbox),
                       min(v.y for v in local_bbox),
                       min(v.z for v in local_bbox)))
    max_point = Vector((max(v.x for v in local_bbox),
                       max(v.y for v in local_bbox),
                       max(v.z for v in local_bbox)))
    
    return {
        "box": [
            (min_point.x + max_point.x)/2,  # center x
            (min_point.y + max_point.y)/2,  # center y
            (min_point.z + max_point.z)/2,  # center z
            (max_point.x - min_point.x)/2,  # x half-length
            0, 0,                           # y orientation
            0, 0,                           # z orientation
            0, (max_point.y - min_point.y)/2,  # y half-length
            0, 0,                           # z orientation
            0, 0, (max_point.z - min_point.z)/2  # z half-length
        ]
    }

def export_glb(obj, path):
    """Export single object as GLB"""
    original_name = obj.name
    obj.name = f"{TILE_BASE_NAME}_{obj.name.split('_')[-2]}_{obj.name.split('_')[-1]}"
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(path, obj.name + ".glb"),
        use_selection=True,
        export_format='GLB'
    )
    obj.name = original_name

def generate_tileset(tile_groups):
    """Generate 3D Tiles compatible JSON hierarchy"""
    tileset = {
        "asset": {"version": "1.0"},
        "geometricError": 1024,
        "root": {
            "boundingVolume": calculate_bounding_volume(bpy.data.objects[0]),
            "geometricError": 512,
            "refine": "ADD",
            "children": []
        }
    }

    for (pi, pj), data in tile_groups.items():
        parent_tile = {
            "boundingVolume": calculate_bounding_volume(data['parent']),
            "geometricError": 256,
            "content": {"uri": f"{data['parent'].name}.glb"},
            "children": []
        }

        for child in data['children']:
            child_data = {
                "boundingVolume": calculate_bounding_volume(child),
                "geometricError": 64,
                "content": {"uri": f"{child.name}.glb"}
            }
            parent_tile["children"].append(child_data)

        tileset["root"]["children"].append(parent_tile)

    return tileset

def process_tiles():
    # Create export directory
    export_dir = bpy.path.abspath(EXPORT_PATH)
    os.makedirs(export_dir, exist_ok=True)

    # Organize tiles into groups
    tile_groups = {}
    
    # Collect all terrain tile objects
    terrain_tiles = [obj for obj in bpy.data.objects]

    # Group tiles into 2x2 parent groups
    for tile in terrain_tiles:
        i, j = get_tile_coordinates(tile)
        parent_i = i // 2
        parent_j = j // 2
        
        if (parent_i, parent_j) not in tile_groups:
            tile_groups[(parent_i, parent_j)] = {
                'children': [],
                'parent': None
            }
        tile_groups[(parent_i, parent_j)]['children'].append(tile)

    # Merge groups and create parent tiles
    for (pi, pj), data in tile_groups.items():
        if len(data['children']) == 4:
            merged = merge_tile_group(data['children'], pi, pj)
            data['parent'] = merged
        else:
            print(f"Warning: Group {pi}-{pj} has {len(data['children'])} tiles")

    # Export all GLBs
    for (pi, pj), data in tile_groups.items():
        if data['parent']:
            export_glb(data['parent'], export_dir)
        for child in data['children']:
            export_glb(child, export_dir)

    # Generate JSON hierarchy
    tileset = generate_tileset(tile_groups)
    with open(os.path.join(export_dir, "tileset.json"), 'w') as f:
        json.dump(tileset, f, indent=2)

    # Cleanup original tiles (optional)
    # for tile in terrain_tiles:
    #     bpy.data.objects.remove(tile)

    print(f"Exported {len(tile_groups)} parent tiles and {len(terrain_tiles)} child tiles")

# Run the processing
process_tiles()