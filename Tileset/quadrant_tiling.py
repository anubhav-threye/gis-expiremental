import bpy
import os
import json
from mathutils import Vector

# Configuration
EXPORT_PATH = r"C:\Users\THREE\Desktop\Blosm\3dtiles"
TILE_BASE_NAME = "Terrain"
QUADRANTS = {
    1: {"x_range": (-8000, 0), "y_range": (-8000, 0)},
    2: {"x_range": (-8000, 0), "y_range": (0, 8000)},
    3: {"x_range": (0, 8000), "y_range": (-8000, 0)},
    4: {"x_range": (0, 8000), "y_range": (0, 8000)}
}
x_segments = 16
y_segments = 16
x_step = (8000.0 - -8000.0) / x_segments  # 1000 units per tile
y_step = (8000.0 - 8000.0) / y_segments

TILE_SIZE = x_step
GRID_SIZE = 8

def get_quadrant_and_udim(obj):
    """Calculate quadrant and UDIM index from object location"""
    center = obj.matrix_world @ Vector(obj.bound_box[0]) + obj.matrix_world @ Vector(obj.bound_box[6])
    center /= 2
    
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

def merge_tiles_group(group_objects, parent_i, parent_j, quadrant):
    """Merge objects using temporary collection"""
    temp_col = bpy.data.collections.new(f"Temp_Quadrant_{quadrant}")
    bpy.context.scene.collection.children.link(temp_col)
    
    copies = []
    for obj in group_objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        temp_col.objects.link(copy)
        copies.append(copy)
    
    bpy.ops.object.select_all(action='DESELECT')
    for copy in copies:
        copy.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    
    bpy.ops.object.join()
    merged_obj = bpy.context.active_object
    merged_obj.name = f"{TILE_BASE_NAME}_{quadrant}_L1_{parent_i:02d}_{parent_j:02d}"
    
    bpy.ops.object.select_all(action='DESELECT')
    merged_obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Cleanup temporary collection
    bpy.data.collections.remove(temp_col)
    
    return merged_obj

def save_quadrant_blend(quadrant, objects, metadata):
    """Save quadrant data to blend file with metadata"""
    temp_scene = bpy.data.scenes.new(f"Quadrant_{quadrant}")
    temp_col = bpy.data.collections.new(f"{quadrant}_Collection")
    temp_scene.collection.children.link(temp_col)

    # Link objects and collect dependencies
    data_blocks = {temp_scene, temp_col}
    for obj in objects:
        temp_col.objects.link(obj)
        data_blocks.add(obj)
        data_blocks.add(obj.data)
        
        if isinstance(obj.data, bpy.types.Mesh):
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    data_blocks.add(mat_slot.material)
                    for node in mat_slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            data_blocks.add(node.image)

    # Store metadata in scene properties
    temp_scene["quadrant_metadata"] = json.dumps(metadata)
    
    # Export path
    os.makedirs(EXPORT_PATH, exist_ok=True)
    output_path = os.path.join(EXPORT_PATH, f"quadrant_{quadrant}.blend")
    
    # Write blend file
    bpy.data.libraries.write(
        filepath=output_path,
        datablocks=data_blocks,
        fake_user=False
    )
    
    # Cleanup
    bpy.data.scenes.remove(temp_scene)
    bpy.data.collections.remove(temp_col)

def calculate_bounding_volume(obj):
    """Calculate bounding volume for 3D Tiles"""
    world_bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
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
            (min_corner.x + max_corner.x)/2,
            (min_corner.y + max_corner.y)/2,
            (min_corner.z + max_corner.z)/2,
            (max_corner.x - min_corner.x)/2, 0, 0,
            0, (max_corner.y - min_corner.y)/2, 0,
            0, 0, (max_corner.z - min_corner.z)/2
        ]
    }

def process_quadrant(quadrant):
    """Process and export a single quadrant"""
    quadrant_objects = [obj for obj in bpy.data.objects 
                       if get_quadrant_and_udim(obj)[0] == quadrant]
    
    metadata = {
        "quadrant": quadrant,
        "tile_size": TILE_SIZE,
        "levels": {
            "L0": {"tiles": [], "bounding_volume": None},
            "L1": {"tiles": [], "bounding_volume": None}
        }
    }

    # Process L0 tiles
    l0_objects = []
    for obj in quadrant_objects:
        q, udim = get_quadrant_and_udim(obj)
        obj.name = f"{TILE_BASE_NAME}_{q}_{udim}"
        l0_objects.append(obj)
        metadata["levels"]["L0"]["tiles"].append({
            "name": obj.name,
            "udim": udim,
            "bounding_volume": calculate_bounding_volume(obj)
        })

    # Process L1 tiles
    l1_objects = []
    for i in range(0, GRID_SIZE, 2):
        for j in range(0, GRID_SIZE, 2):
            group = [obj for obj in quadrant_objects 
                    if (i <= (get_quadrant_and_udim(obj)[1] - 1001) % 10 < i+2) and
                       (j <= (get_quadrant_and_udim(obj)[1] - 1001) // 10 < j+2)]
            
            if len(group) == 4:
                merged = merge_tiles_group(group, i, j, quadrant)
                l1_objects.append(merged)
                metadata["levels"]["L1"]["tiles"].append({
                    "name": merged.name,
                    "children": [obj.name for obj in group],
                    "bounding_volume": calculate_bounding_volume(merged)
                })

    # Calculate quadrant bounding volume
    metadata["levels"]["L0"]["bounding_volume"] = QUADRANTS[quadrant]
    metadata["levels"]["L1"]["bounding_volume"] = QUADRANTS[quadrant]

    # Save quadrant blend with metadata
    save_quadrant_blend(quadrant, l0_objects + l1_objects, metadata)
    
    # Cleanup merged objects
    for obj in l1_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

# Process all quadrants
for quadrant in QUADRANTS:
    process_quadrant(quadrant)

print("All quadrants processed successfully")