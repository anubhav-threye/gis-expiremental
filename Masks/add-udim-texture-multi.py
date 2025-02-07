import bpy

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
