import os
import bpy
from mathutils import Vector


mesh_base_name = 'mesh_base'
# Configure these variables according to your grid setup
# Terrain bounding box parameters (from original script)
x_min = -7999.99951171875
x_max = 8000.0
y_min = -8000.00048828125
y_max = 8000.0

x_segments = 16
y_segments = 16

x_step = (x_max - x_min) / x_segments  # 1000.0 units per segment
y_step = (y_max - y_min) / y_segments  # 1000.0 units per segment
output_dir = r"C:\Work\Threye\GIS\UDIM"  # Output directory (relative to the blend file)
QUADRANT_MAP = {1: 2, 2: 4, 3: 1, 4: 3}
def calculate_udim_quadrant(obj):
    print("Calculate UDIM and quadrant based on object's center position.")
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(bbox_corners, Vector()) / len(bbox_corners)
    x, y = center.x, center.y

    # Calculate grid indices
    i = int((x - x_min) // x_step)
    i = max(0, min(15, i))
    j = int((y - y_min) // y_step)
    j = max(0, min(15, j))

    # Determine quadrant
    if i < 8 and j < 8:
        quadrant = 1
    elif i < 8 and j >= 8:
        quadrant = 2
    elif i >= 8 and j < 8:
        quadrant = 3
    else:
        quadrant = 4

    # Calculate local indices
    if quadrant == 1:
        local_i, local_j = i, j
    elif quadrant == 2:
        local_i, local_j = i, j - 8
    elif quadrant == 3:
        local_i, local_j = i - 8, j
    else:
        local_i, local_j = i - 8, j - 8

    # Calculate UDIM with 90-degree CCW rotation
    udim = 1001 + (7 - local_i) * 10 + local_j
    new_quadrant = QUADRANT_MAP.get(quadrant, quadrant)
    return new_quadrant, udim

def export_object(obj, quadrant, udim):
    """Export object to the appropriate blend file."""
    filename = f"{quadrant}_{udim}.blend"
    filepath = bpy.path.abspath(os.path.join(output_dir, filename))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Save the object's transform
    original_location = obj.location.copy()
    original_rotation = obj.rotation_euler.copy()
    original_scale = obj.scale.copy()

    # Create a new temporary scene and collection
    collection_name = f"{quadrant}_{udim}"
    export_collection = bpy.data.collections.new(collection_name)
    temp_scene = bpy.data.scenes.new(f"TEMP_SCENE_{quadrant}_{udim}")

    # Link the collection to the temporary scene
    temp_scene.collection.children.link(export_collection)

    # Link the object to the temporary collection
    export_collection.objects.link(obj)

    # Collect data blocks to export
    data_blocks = {
        temp_scene,
        export_collection,
        obj,
        obj.data,
    }

    # Include materials and mesh data
    if obj.data:
        if isinstance(obj.data, bpy.types.Mesh):
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    data_blocks.add(mat_slot.material)

    # Write to blend file (only the temporary scene/collection)
    bpy.data.libraries.write(filepath, data_blocks, fake_user=True)

    # Restore the object's transform and original collection links
    obj.location = original_location
    obj.rotation_euler = original_rotation
    obj.scale = original_scale

    # Cleanup: Remove temporary scene and collection
    bpy.data.scenes.remove(temp_scene)
    bpy.data.collections.remove(export_collection)
def main():
    # Process all mesh objects in the scene
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or not obj.name.startswith(mesh_base_name):
            continue

        quadrant, udim = calculate_udim_quadrant(obj)
        export_object(obj, quadrant, udim)

main()