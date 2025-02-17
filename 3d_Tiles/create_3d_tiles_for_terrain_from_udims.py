import bpy
import os
import bmesh
import mathutils
import re
# Configuration
EXPORT_PATH = rf"C:\Users\THREE\Desktop\Blosm\3dtiles\glb"  # Blender relative export path
# JSON_PATH = r"C:\Users\THREE\Desktop\Blosm"

TERRAIN_DIR = rf"C:\Users\THREE\Desktop\Blosm\Final Terrain 16 Files (1)\Final Terrain 16 Files"
# BUILDIN_DIR = rf"C:\Users\THREE\Desktop\Blosm\3dtiles\1034\buildings"
export_settings = {
    "use_selection": True,
    "export_extras": True,  # Custom properties
    "export_yup": True,  # +Y Up
    "export_apply": True,  # Apply modifiers
    "export_attributes": False,  # No vertex colors
    "export_image_format": "JPEG",
    "export_jpeg_quality": 100,
    "export_skins": False,  # No skinning
    "export_morph": False,  # No shape keys
    "export_animations": False,  # No animation
}
def export_terrain_glb(terrain_tile, directory):
    
    # Select only target object
    bpy.ops.object.select_all(action='DESELECT')
    terrain_tile.select_set(True)
    # Apply All Transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    export_dir = os.path.join(EXPORT_PATH, f"{directory}", f"{terrain_tile.name}.glb")
    os.makedirs(export_dir, exist_ok=True)
    # Export
    bpy.ops.export_scene.gltf(
        filepath=export_dir,
        **export_settings
    )
    return
    
# def get_quadrant_udim_building(terrain_tile):
# # (path, f"{obj.name}.glb")
#     build_file = os.path.join(rf"{TERRAIN_DIR}/{terrain_tile.name}.blend")
#     try:
#         # load the building
#         with bpy.data.libraries.load(build_file, link=False) as (data_from, data_to):
#             if terrain_tile.name in data_from.collections:
#                 data_to.collections = [terrain_tile.name]
#             else:
#                 data_to.collections = []
#         build_col = data_to.collections[0]
#         return build_col
#     except RuntimeError:
#         print(f"Error: Building collection not found {terrain_tile.name}")
#         return None

# def join_building_and_center_to_tile(terrain_tile, building_col):
#     join = []
#     for building_obj in building_col:
#     # Copy and join objects
#         join.append(building_obj)
    
#     bpy.ops.object.select_all(action='DESELECT')
#     for build_obj in join:
#         build_obj.select_set(True)

#     bpy.context.view_layer.objects.active = join[0]
#     bpy.ops.object.join()
#     merged_build_obj = bpy.context.active_object
#     merged_build_obj.name = f"{build_obj.name}_{terrain_tile.name}}"
    
# def shift_obj_to_origin(tile):
#     print("type",tile.type)
#     print("name",tile.name)
#     # Deselect all objects
#     bpy.ops.object.select_all(action='DESELECT')
#     match = re.match(r"(\d+)_(\d{4})", tile.name)
#     if match:
#         quadrant = int(match.group(1))
#         udim = int(match.group(2))

#         x_shift = ((udim % 10)*1000) + 500
#         y_shift = (((udim // 100) % 10) * 1000) + 500


#     if quadrant == 1:
#         x_shift = -x_shift
#     elif quadrant == 3:
#         x_shift = -x_shift
#         y_shift = -y_shift
#     elif quadrant == 4:
#         y_shift = -y_shift

#     tile.select_set(True)
#     bpy.context.view_layer.objects.active = tile

#     bpy.ops.object.mode_set(mode='EDIT')
#     # Get a BMesh representation of the mesh data
#     bm = bmesh.from_edit_mesh(tile.data)
#     # Define the offset vector (move 1 unit along the X-axis)
#     offset = mathutils.Vector((x_shift, y_shift, 0.0))
#     # Iterate over all vertices and move each by the offset
#     for vert in bm.verts:
#         vert.co += offset

#     # Update the mesh with the modified data
#     bmesh.update_edit_mesh(tile.data)
#     # Return to Object Mode
#     bpy.ops.object.mode_set(mode='OBJECT')
#     return
def process_files(target_dir):
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".blend"):
                filepath = os.path.join(root, file)
                
                # Open the target blend file
                bpy.ops.wm.open_mainfile(filepath=filepath)
                
                terrain_tiles = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]

                for terrain_tile in terrain_tiles:
                    
                    # # get building collection this file's
                    # building_col = get_quadrant_udim_building(terrain_tile)
                    # join_building_and_center_to_tile(terrain_tile, building_col)
                    # shift_obj_to_origin(terrain_tile)
                    export_terrain_glb(terrain_tile, file[:2])

                print(f"Processed: {filepath}")

# Run the processing
process_files(TERRAIN_DIR)