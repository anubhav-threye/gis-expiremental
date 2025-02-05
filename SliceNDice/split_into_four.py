import bpy
from mathutils import Vector

def bbox(ob):
    """Get the world-space coordinates of the object's bounding box corners."""
    return [ob.matrix_world @ Vector(corner) for corner in ob.bound_box]

def get_bbox_axes(ob):
    """Get the minimum and maximum coordinates along each axis from the bounding box."""
    bbox_corners = bbox(ob)
    xs = [v.x for v in bbox_corners]
    ys = [v.y for v in bbox_corners]
    zs = [v.z for v in bbox_corners]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

def bisect(obj, plane_point, plane_normal, inner=False):
    """Bisect the object along a plane defined by a point and a normal."""
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
        plane_co=plane_point,
        plane_no=plane_normal,
        use_fill=True,
        clear_inner=inner,
        clear_outer=not inner
    )
    
    # Return to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj

def slice_mesh(obj, x_segments=2, y_segments=2):
    if obj.type != 'MESH':
        return None

    # Get bounding box axes
    (x_min, x_max), (y_min, y_max), _ = get_bbox_axes(obj)
    
    # Calculate step sizes
    x_step = (x_max - x_min) / x_segments
    y_step = (y_max - y_min) / y_segments
    
    # Calculate slicing planes
    x_planes = [x_min + i * x_step for i in range(1, x_segments)]
    y_planes = [y_min + i * y_step for i in range(1, y_segments)]
    
    # Start with the original object
    parts = [obj]
    
    # Bisect along X planes
    for x_plane in x_planes:
        new_parts = []
        for part in parts:
            # Prepare plane data
            plane_point = Vector((x_plane, 0, 0))
            plane_normal = Vector((1, 0, 0))

            # Copy the part for the positive side
            pos_part = part.copy()
            pos_part.data = part.data.copy()
            bpy.context.collection.objects.link(pos_part)
            bisect(pos_part, plane_point, plane_normal, inner=False)
            
            # Bisect the original part for the negative side
            bisect(part, plane_point, plane_normal, inner=True)
            
            new_parts.extend([part, pos_part])
        parts = new_parts

    # Bisect along Y planes
    final_parts = []
    for part in parts:
        sub_parts = [part]
        for y_plane in y_planes:
            temp_parts = []
            for sub_part in sub_parts:
                # Prepare plane data
                plane_point = Vector((0, y_plane, 0))
                plane_normal = Vector((0, 1, 0))
                
                # Copy the sub_part for the positive side
                pos_part = sub_part.copy()
                pos_part.data = sub_part.data.copy()
                bpy.context.collection.objects.link(pos_part)
                bisect(pos_part, plane_point, plane_normal, inner=False)
                
                # Bisect the sub_part for the negative side
                bisect(sub_part, plane_point, plane_normal, inner=True)
                
                temp_parts.extend([sub_part, pos_part])
            sub_parts = temp_parts
        final_parts.extend(sub_parts)
    
    # Remove original object
    if obj in bpy.context.scene.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    
    # Rename parts
    for i, part in enumerate(final_parts):
        part.name = f"{obj.name}_Sliced_Part_{i+1}"
    
    return final_parts

def slice_all_meshes(x_segments=2, y_segments=2):
    original_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in original_meshes:
        print(f"Slicing: {obj.name}")
        slice_mesh(obj, x_segments, y_segments)

# Run the script with the desired number of segments
slice_all_meshes(x_segments=2, y_segments=2)
