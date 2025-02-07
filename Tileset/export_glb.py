import bpy
import os

# Set output directory (change this to your preferred path)
# output_dir = bpy.path.abspath("//GLB_Exports")  # Saves in a subfolder next to your .blend file
output_dir = r"E:\Projects\GIS\GIS-WSL\gis-expiremental\data\3d_tiles\exported_glb"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Store original selection
original_selection = bpy.context.selected_objects.copy()

# Export settings
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

# Iterate through all mesh objects
for obj in bpy.data.objects:
    if obj.type == "MESH":
        # Deselect all objects
        bpy.ops.object.select_all(action="DESELECT")

        # Select current object
        obj.select_set(True)

        # Create file path
        filename = f"{obj.name}.glb"
        filepath = os.path.join(output_dir, filename)

        # Export GLB
        bpy.ops.export_scene.gltf(filepath=filepath, **export_settings)

        print(f"Exported: {filename}")

# Restore original selection
bpy.ops.object.select_all(action="DESELECT")
for obj in original_selection:
    obj.select_set(True)

print("Export completed!")
