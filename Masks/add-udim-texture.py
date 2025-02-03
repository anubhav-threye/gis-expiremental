import bpy


def remove_material_from_mesh(mesh):
    # Check if the mesh has a material assigned
    if mesh.data.materials:
        # Remove the material from the mesh
        mesh.data.materials.clear()


def add_image_texture_material(mesh, path, mask_name):
    # Add material to the mesh
    material = bpy.data.materials.new(name=f"{material_name_prefix}_{mesh.name}")

    # Set base color to image texture
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    texImage = material.node_tree.nodes.new("ShaderNodeTexImage")
    texImage.image = bpy.data.images.load(f"{path}/{mask_name}_{mesh.name}.png")
    material.node_tree.links.new(bsdf.inputs["Base Color"], texImage.outputs["Color"])

    # Assign material to mesh
    mesh.data.materials.append(material)


# UDIM files path
path = r"E:\Projects\GIS\GIS-WSL\gis-expiremental\Masks\data\Bulit up\4k UDIM"
# UDIM Image file prefix
mask_name = "bulitup"
# Material renaming prefix
material_name_prefix = "BuiltUp"

# Get all the meshes from the collection
for mesh in bpy.context.collection.objects:
    # Check if the object is a mesh
    if mesh.type == "MESH":
        # Remove the material from the mesh
        remove_material_from_mesh(mesh)

        # Add the material from the mesh
        add_image_texture_material(mesh, path, mask_name)
