import bpy
from mathutils import Vector

terrain_bbox = (Vector((-100.0, -100.00000762939453, 0.0145195871591568)), Vector((100.0, -100.00000762939453, 0.0145195871591568)), Vector((-100.0, 100.0, 0.0145195871591568)), Vector((-100.0, -100.00000762939453, 18.9511661529541)))                                                                                                                           
x_segments = 8  # 16 slices along the X axis
y_segments = 8  # 16 slices along the Y axis

# Ensure we are creating planes that exactly match the grid's divisions
x_start, x_end = terrain_bbox[0].x, terrain_bbox[1].x
y_start, y_end = terrain_bbox[0].y, terrain_bbox[2].y

# Calculate the step size between each plane
x_step = (x_end - x_start) / x_segments
y_step = (y_end - y_start) / y_segments
# Terrain bounding box parameters (from original script)
x_min = -100.0
x_max = 100.0
y_min = -100.00000762939453
y_max = 100.0


# Quadrant remapping: 1→2, 2→4, 3→1, 4→3
QUADRANT_MAP = {1: 2, 2: 4, 3: 1, 4: 3}

def rename_sliced_objects():
    print("##################### Rename ######################")
    
    for obj in bpy.context.scene.objects:
        
        # Calculate object's center (using bounding box)
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        center = sum(bbox_corners, Vector()) / len(bbox_corners)
        x, y = center.x, center.y
        
        # Calculate grid indices (i, j)
        i = int((x - x_min) // x_step)
        i = max(0, min(15, i))  # Clamp to 0-15
        
        j = int((y - y_min) // y_step)
        j = max(0, min(15, j))  # Clamp to 0-15
        
        # Determine quadrant based on grid indices
        if i < 8 and j < 8:
            quadrant = 1
        elif i < 8 and j >= 8:
            quadrant = 2
        elif i >= 8 and j < 8:
            quadrant = 3
        else:
            quadrant = 4
        
        # Calculate local indices within the quadrant
        if quadrant == 1:
            local_i = i
            local_j = j
        elif quadrant == 2:
            local_i = i
            local_j = j - 8
        elif quadrant == 3:
            local_i = i - 8
            local_j = j
        else:  # quadrant 4
            local_i = i - 8
            local_j = j - 8
        
        # Compute new UDIM (1001 + row*10 + column)
        # new_udim = 1001 + (local_j * 10) + local_i
        new_udim = 1001 + (7 - local_i) * 10 + local_j # ccw 90 DEGREES

        new_quadrant = QUADRANT_MAP.get(quadrant, quadrant)
        # Rebuild the object name
        # base_name = obj.name[:match.start(1)-1]  # Everything before the counter
        new_name = f"{new_quadrant}_{new_udim}"
        
        print(f"Renamed {obj.name} -> {new_name}")

        # Update object and mesh names
        obj.name = new_name
        if obj.data:
            obj.data.name = new_name

rename_sliced_objects()