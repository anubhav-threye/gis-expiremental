import bpy
import re
from mathutils import Vector

# Terrain bounding box parameters (from original script)
x_min = -7999.99951171875
x_max = 8000.0
y_min = -8000.00048828125
y_max = 8000.0

x_segments = 16
y_segments = 16

x_step = (x_max - x_min) / x_segments  # 1000.0 units per segment
y_step = (y_max - y_min) / y_segments  # 1000.0 units per segment

# Quadrant remapping: 1→2, 2→4, 3→1, 4→3
QUADRANT_MAP = {1: 2, 2: 4, 3: 1, 4: 3}

def rename_sliced_objects():
    print("##################### Rename ######################")
    # Regex to extract counter, original quadrant, and original UDIM
    # pattern = re.compile(r'_(\d+)_(\d+)_(\d+)$')
    
    for obj in bpy.context.scene.objects:
        # if not obj.name.startswith("Var_2_hotel_base") or obj.hide_viewport:
        #     continue
        # match = pattern.search(obj.name)
        # if not match:
        #     continue  # Skip objects that don't match the pattern
        
        # counter = match.group(1)
        # orig_quadrant = int(match.group(2))
        # orig_udim = match.group(3)
        
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
        
        # Update object and mesh names
        obj.name = new_name
        if obj.data:
            obj.data.name = new_name

        # Ensure the object has a material
        if obj.data.materials:
            # Access the first material slot
            material = obj.data.materials[0]
            material.name = new_name

            # Check if the material uses nodes (required for textures)
            if material.use_nodes:
                # Get material's First nodes
                node = material.node_tree.nodes[0]
                # Check if the node is a texture node
                if node.type == 'TEX_IMAGE':
                    # Rename the texture
                    node.image.name = new_name
                elif node.type == 'BSDF_PRINCIPLED':
                    # Get the Base Color input
                    base_color_input = node.inputs['Base Color']
                    
                    # Check if the Base Color input is connected to an Image Texture node
                    if base_color_input.is_linked:
                        # Get the connected Image Texture node
                        image_texture_node = base_color_input.links[0].from_node
                        
                        # Ensure the connected node is an Image Texture node
                        if image_texture_node.type == 'TEX_IMAGE':
                            # Rename the image texture
                            image_texture_node.image.name = new_name
rename_sliced_objects()