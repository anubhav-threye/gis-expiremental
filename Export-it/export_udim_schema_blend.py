import os
import bpy
from mathutils import Vector

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
    return quadrant, udim

def export_object(obj, quadrant, udim):
    """Export object to the appropriate blend file."""
    filename = f"{quadrant}_{udim}.blend"
    filepath = bpy.path.abspath(os.path.join(output_dir, filename))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Save the object's transform
    original_location = obj.location.copy()
    original_rotation = obj.rotation_euler.copy()
    original_scale = obj.scale.copy()

    # Create a new collection with the same name as the blend file
    collection_name = f"{quadrant}_{udim}"
    export_collection = bpy.data.collections.new(collection_name)

    # Link the collection to the scene temporarily
    bpy.context.scene.collection.children.link(export_collection)

    # Link the object to the collection
    export_collection.objects.link(obj)

    # Collect all related data blocks
    data_blocks = set()
    data_blocks.add(export_collection)  # Include the collection
    data_blocks.add(obj)  # Include the object
    if obj.data:
        data_blocks.add(obj.data)
        if isinstance(obj.data, bpy.types.Mesh):
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    data_blocks.add(mat_slot.material)

    # Write data to blend file
    bpy.data.libraries.write(filepath, data_blocks, fake_user=True)

    # Restore the object's transform
    obj.location = original_location
    obj.rotation_euler = original_rotation
    obj.scale = original_scale

    # Clean up the temporary collection
    bpy.context.scene.collection.children.unlink(export_collection)
    bpy.data.collections.remove(export_collection)

    # Ensure the collection is linked to the view layer in the exported file
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.collections = [collection_name]

    # Link the collection to the view layer in the exported file
    bpy.ops.wm.open_mainfile(filepath=filepath)
    exported_collection = bpy.data.collections.get(collection_name)
    if exported_collection:
        bpy.context.scene.collection.children.link(exported_collection)
    bpy.ops.wm.save_mainfile()

def main():
    # Process all mesh objects in the scene
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue

        quadrant, udim = calculate_udim_quadrant(obj)
        export_object(obj, quadrant, udim)

main()