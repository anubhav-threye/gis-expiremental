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

# Create temporary collection
merged_col = bpy.data.collections.new(f"Merged_{x_segments/4}X{y_segments/4}")
bpy.context.scene.collection.children.link(merged_col)

def get_tile_coordinates(obj):
    """Calculate original grid coordinates from object's bounding box"""
    bbox_corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    center = sum(bbox_corners, Vector()) / len(bbox_corners)
    i = int((center.x - x_min) // x_step)
    j = int((center.y - y_min) // y_step)
    return max(0, min(i, x_segments-1)), max(0, min(j, y_segments-1))

def merge_tiles_group(group_objects, parent_i, parent_j, quadrant):
    """Merge objects using Blender's join operator while keeping temp collection"""

    
    # Copy objects to temporary collection
    copies = []
    for obj in group_objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        merged_col.objects.link(copy)
        copies.append(copy)
    
    # Select and join copies
    bpy.ops.object.select_all(action='DESELECT')
    for copy in copies:
        copy.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    
    bpy.ops.object.join()
    merged_obj = bpy.context.active_object
    merged_obj.name = f"{TILE_BASE_NAME}_L1_{parent_i:02d}_{parent_j:02d}"
    
    # Apply transformations (rotation/scale) but keep world position
    bpy.ops.object.select_all(action='DESELECT')
    merged_obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Weld vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')
    # Link merged object to main collection
    # bpy.context.scene.collection.objects.link(merged_obj)
    
    # Unlink from temp collection (optional)
    # temp_col.objects.unlink(merged_obj)

    # Store metadata
    child_names = [obj.name for obj in group_objects]
    merged_obj["child_tiles"] = ",".join(child_names)
    merged_obj["quadrant"] = str(quadrant)

    return merged_obj
def calculate_bounding_volume(obj):
    """Calculate bounding volume in world coordinates"""
    world_bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_corner = Vector((
        min(v.x for v in world_bbox),
        min(v.y for v in world_bbox),
        min(v.z for v in world_bbox)
    ))
    max_corner = Vector((
        max(v.x for v in world_bbox),
        max(v.y for v in world_bbox),
        max(v.z for v in world_bbox)
    ))
    
    return {
        "box": [
            (min_corner.x + max_corner.x)/2,  # center x
            (min_corner.y + max_corner.y)/2,  # center y
            (min_corner.z + max_corner.z)/2,  # center z
            (max_corner.x - min_corner.x)/2, 0, 0,  # x half-length
            0, (max_corner.y - min_corner.y)/2, 0,   # y half-length
            0, 0, (max_corner.z - min_corner.z)/2    # z half-length
        ]
    }

def export_glb(obj, path):
    """Export GLB with proper transform handling"""
    # Reset location (keep geometry in place)
    original_location = obj.location.copy()
    obj.location = (0, 0, 0)
    
    # Select only target object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    
    # Export
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(path, f"{obj.name}.glb"),
        use_selection=True,
        export_format='GLB',
        export_yup=True
    )
    
    # Restore original location
    obj.location = original_location
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

def save_merged_collection():
    """Save the merged collection to a new blend file"""
    # Ensure the collection exists
    if not merged_col:
        print("No merged collection found")
        return
    temp_scene = bpy.data.scenes.new(f"TEMP_SCENE")
    temp_scene.collection.children.link(merged_col)

    file_name = rf"{merged_col.name}.blend"
    # Create output path
    output_path = os.path.join(EXPORT_PATH, file_name)

    # Collect all data blocks to save
    data_blocks = {temp_scene, merged_col}
    
    # Add all objects in the collection and their dependencies
    for obj in merged_col.objects:
        data_blocks.add(obj)
        data_blocks.add(obj.data)
        
        # # Add materials and textures
        # for mat in obj.data.materials:
        #     data_blocks.add(mat)
        #     for tex in mat.texture_slots:
        #         if tex and tex.texture:
        #             data_blocks.add(tex.texture)
        if isinstance(obj.data, bpy.types.Mesh):
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    data_blocks.add(mat_slot.material)
                    # Include textures/images
                    for node in mat_slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            data_blocks.add(node.image)

    # Save to blend file
    bpy.data.libraries.write(
        filepath=output_path,
        datablocks=data_blocks,
        fake_user=False
    )
    bpy.data.scenes.remove(temp_scene)
    bpy.data.collections.remove(merged_col)
    
    print(f"Saved merged collection to {output_path}")

def process_tiles():
    export_dir = bpy.path.abspath(EXPORT_PATH)
    os.makedirs(export_dir, exist_ok=True)
    
    # Get all terrain tiles (assuming they're named correctly)
    terrain_tiles = [obj for obj in bpy.data.objects]
    
    # Create parent-child structure
    tile_hierarchy = {}
    for tile in terrain_tiles:
        i, j = get_tile_coordinates(tile)
        # calculate quadrant
        if i < 8 and j < 8:
            quadrant = 1
        elif i < 8 and j >= 8:
            quadrant = 2
        elif i >= 8 and j < 8:
            quadrant = 3
        else:
            quadrant = 4
        parent_i = i // 2
        parent_j = j // 2
        
        key = (parent_i, parent_j)
        if key not in tile_hierarchy:
            tile_hierarchy[key] = {
                'children': [],
                'parent': None
            }
        tile_hierarchy[key]['children'].append(tile)
    

    # Merge and export
    for (pi, pj), data in tile_hierarchy.items():
        if len(data['children']) == 4:
            # Merge group
            parent = merge_tiles_group(data['children'], pi, pj, quadrant)
            data['parent'] = parent
            
            # # Export children
            # for child in data['children']:
            #     export_glb(child, export_dir)
            
            # # Export parent
            # export_glb(parent, export_dir)
            
            # Position parent at children's center
            parent.location = sum((obj.location for obj in data['children']), Vector()) / 4
    
    # Generate JSON hierarchy
    tileset = {
        "asset": {"version": "1.0"},
        "geometricError": 2048,
        "root": {
            "children": []
        }
    }
    
    for (pi, pj), data in tile_hierarchy.items():
        if data['parent']:
            parent_entry = {
                "boundingVolume": calculate_bounding_volume(data['parent']),
                "geometricError": 512,
                "content": {"uri": f"{data['parent'].name}.glb"},
                "children": [
                    {
                        "boundingVolume": calculate_bounding_volume(child),
                        "geometricError": 128,
                        "content": {"uri": f"{child.name}.glb"}
                    } for child in data['children']
                ]
            }
            tileset["root"]["children"].append(parent_entry)
    file_name = rf"{merged_col.name}.json"
    with open(os.path.join(export_dir, file_name), 'w') as f:
        json.dump(tileset, f, indent=2)
    
    print(f"Processed {len(tile_hierarchy)} parent tiles")
    # After generating JSON and processing tiles
    save_merged_collection() 
# Run the processing
process_tiles()