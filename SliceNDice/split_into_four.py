import bpy
from mathutils import Vector

def calculate_center(obj):
    """Calculate the center of an object's vertices in world space."""
    mesh = obj.data
    world_verts = [obj.matrix_world @ v.co for v in mesh.vertices]
    return sum(world_verts, Vector()) / len(world_verts)

def bisect(obj, axis, inner=False):
    """Slice an object along a given axis, using its own center."""
    center = calculate_center(obj)
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select and activate the object to bisect
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Enter Edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Ensure only the object's geometry is selected
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Perform the bisect operation
    bpy.ops.mesh.bisect(
        plane_co=center,
        plane_no=axis,
        use_fill=True,
        clear_inner=inner,
        clear_outer=not inner
    )
    
    # Return to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj

def slice_mesh_into_four(obj):
    if obj.type != 'MESH':
        return None

    # Copy the object and its mesh data to ensure uniqueness
    x_outer = obj.copy()
    x_outer.data = obj.data.copy()
    bpy.context.collection.objects.link(x_outer)
    
    # Bisect along the X-axis (negative side)
    bisect(x_outer, Vector((1, 0, 0)), inner=False)
    
    # Create another copy for the positive side of the X-axis
    x_inner = obj.copy()
    x_inner.data = obj.data.copy()
    bpy.context.collection.objects.link(x_inner)
    bisect(x_inner, Vector((1, 0, 0)), inner=True)

    # Prepare to collect final parts
    final_parts = []

    # Bisect each X-part along the Y-axis
    for part in [x_outer, x_inner]:
        # Negative side of Y-axis
        y_outer = part.copy()
        y_outer.data = part.data.copy()
        bpy.context.collection.objects.link(y_outer)
        bisect(y_outer, Vector((0, 1, 0)), inner=False)
        
        # Positive side of Y-axis
        y_inner = part.copy()
        y_inner.data = part.data.copy()
        bpy.context.collection.objects.link(y_inner)
        bisect(y_inner, Vector((0, 1, 0)), inner=True)
        
        final_parts.extend([y_outer, y_inner])
        
        # Remove the intermediate part
        bpy.data.objects.remove(part, do_unlink=True)

    # Delete the original object
    bpy.data.objects.remove(obj, do_unlink=True)
    
    # Rename parts
    for i, part in enumerate(final_parts):
        part.name = f"{obj.name}_Sliced_Part_{i+1}"
    
    return final_parts
def slice_all_meshes():
    original_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in original_meshes.copy():  # Use copy to avoid modifying the list while iterating
        print(f"Slicing: {obj.name}")
        slice_mesh_into_four(obj)

# Run the script
slice_all_meshes()