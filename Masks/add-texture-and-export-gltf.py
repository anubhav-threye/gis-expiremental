import bpy
import os

# UDIM files path
diffuse_path = (
    r"E:\Projects\GIS\GIS-WSL\gis-expiremental\Masks\data\Bulit up\4k UDIM\Diffuse"
)
normal_path = (
    r"E:\Projects\GIS\GIS-WSL\gis-expiremental\Masks\data\Bulit up\4k UDIM\Normal"
)
roughness_path = (
    r"E:\Projects\GIS\GIS-WSL\gis-expiremental\Masks\data\Bulit up\4k UDIM\Roughness"
)
# Texture file prefix
diffuse_prefix = "Q1_Diffuse"
normal_prefix = "Q1_Normal"
roughness_prefix = "Q1_Roughness"

# File Format
file_format = "jpg"


def initial_setup():
    # Disable Automatically Pack Resources
    bpy.data.use_autopack = True
    # Unpack all resources
    bpy.ops.file.unpack_all(method="USE_LOCAL")


def remove_material_from_mesh(mesh):
    # Check if the mesh has a material assigned
    if mesh.data.materials:
        # Remove the material from the mesh
        mesh.data.materials.clear()


def get_udim(mesh_name):
    _quad, udim = mesh_name.split("_")
    return udim


def add_principled_bsdf_material(mesh):
    # Add material to the mesh
    material = bpy.data.materials.new(name=f"{mesh.name}")

    # Set base color to white
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]

    # Assign material to mesh
    mesh.data.materials.append(material)
    return bsdf, material


def add_diffuse_image_texture(bsdf, material, udim, path, mask_name_prefix):
    # Set base color to image texture
    texImage = material.node_tree.nodes.new("ShaderNodeTexImage")
    texImage.image = bpy.data.images.load(
        f"{path}/{mask_name_prefix}_{udim}.{file_format}"
    )
    material.node_tree.links.new(bsdf.inputs["Base Color"], texImage.outputs["Color"])


def add_normal_image_texture(bsdf, material, udim, path, mask_name_prefix):
    texImage = material.node_tree.nodes.new("ShaderNodeTexImage")
    texImage.image = bpy.data.images.load(
        f"{path}/{mask_name_prefix}_{udim}.{file_format}"
    )
    texImage.image.colorspace_settings.name = "Non-Color"

    # Create a normal map
    normal_map = material.node_tree.nodes.new("ShaderNodeNormalMap")

    # Attach mater
    material.node_tree.links.new(bsdf.inputs["Normal"], normal_map.outputs["Normal"])
    material.node_tree.links.new(normal_map.inputs["Color"], texImage.outputs["Color"])


def add_roughness_image_texture(bsdf, material, udim, path, mask_name_prefix):
    # Set base color to image texture
    texImage = material.node_tree.nodes.new("ShaderNodeTexImage")
    texImage.image = bpy.data.images.load(
        f"{path}/{mask_name_prefix}_{udim}.{file_format}"
    )
    material.node_tree.links.new(bsdf.inputs["Roughness"], texImage.outputs["Color"])


# Unpack resources
initial_setup()

# Get all the meshes from the collection
for mesh in bpy.context.selected_objects:
    # Check if the object is a mesh
    if mesh.type == "MESH":
        # Remove the material from the mesh
        remove_material_from_mesh(mesh)

        # Create Material
        bsdf, material = add_principled_bsdf_material(mesh)
        # UDIM number
        udim = get_udim(mesh.name)

        # Add the material from the mesh
        add_diffuse_image_texture(
            bsdf, material, udim, path=diffuse_path, mask_name_prefix=diffuse_prefix
        )
        add_normal_image_texture(
            bsdf, material, udim, path=normal_path, mask_name_prefix=normal_prefix
        )
        add_roughness_image_texture(
            bsdf, material, udim, path=roughness_path, mask_name_prefix=roughness_prefix
        )


# Set output directory (change this to your preferred path)
# output_dir = bpy.path.abspath("//GLB_Exports")  # Saves in a subfolder next to your .blend file
output_dir = r"/home/finker/development/tile/Tiles"

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
