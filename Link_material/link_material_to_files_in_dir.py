import bpy
import os
import sys

def create_material(material_name, base_color_image_path, normal_image_path):
    # Load the images into the current blend file's data
    base_color_image = bpy.data.images.load(base_color_image_path)
    normal_image = bpy.data.images.load(normal_image_path)
    
    # Create a new material
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    
    # Clear existing nodes (for safety, in case template has some)
    material.node_tree.nodes.clear()
    
    # Create necessary nodes
    bsdf = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    
    tex_base_color = material.node_tree.nodes.new("ShaderNodeTexImage")
    tex_base_color.image = base_color_image
    tex_base_color.location = (-400, 200)
    
    tex_normal = material.node_tree.nodes.new("ShaderNodeTexImage")
    tex_normal.image = normal_image
    tex_normal.location = (-400, -200)
    
    normal_map = material.node_tree.nodes.new("ShaderNodeNormalMap")
    normal_map.location = (-200, -200)
    
    # Link nodes
    links = material.node_tree.links
    links.new(bsdf.inputs['Base Color'], tex_base_color.outputs['Color'])
    links.new(normal_map.inputs['Color'], tex_normal.outputs['Color'])
    links.new(bsdf.inputs['Normal'], normal_map.outputs['Normal'])
    
    # Set material output
    output = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
    output.location = (200, 0)
    links.new(output.inputs['Surface'], bsdf.outputs['BSDF'])
    
    return material

def get_linked_material(source_blend, material_name):
    # Append material from source blend file
    material = bpy.data.materials.get(material_name)
    if not material:
        directory = os.path.join(source_blend, 'Material').replace(os.sep, '/')
        try:
            # Link the material
            bpy.ops.wm.link(
                directory=directory, 
                filename=material_name,
                link=True
            )
        except RuntimeError:
            print(f"Error: Material '{material_name}' not found in {source_blend}")
            return None
        material = bpy.data.materials.get(material_name)
    return material

def assign_material_to_meshes(material):
    # Assign material to all mesh objects (replaces existing materials)
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            # Clear existing materials
            obj.data.materials.clear()
            # Assign the new material directly
            obj.data.materials.append(material)

def process_files(source_blend, material_name, target_dir):
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".blend"):
                filepath = os.path.join(root, file)
                
                # Open the target blend file
                bpy.ops.wm.open_mainfile(filepath=filepath)
                
                # get material within this file's context
                material = get_linked_material(source_blend, material_name)

                
                # Get the linked material
                material = bpy.data.materials[material_name]
                if not material:
                    print(f"Material creation failed for {material_name} in {filepath}.")
                    continue
                
                # Assign material and save
                assign_material_to_meshes(material)
                # Clean up unused data blocks
                # cleanup_unused_data()

                # Purge unused data
                # purge_unused_data()
                bpy.ops.wm.save_mainfile()
                print(f"Processed: {filepath}")

def cleanup_unused_data():
    # Purge unused data blocks (images, materials, etc.)
    for block in (bpy.data.images, bpy.data.materials, bpy.data.textures, bpy.data.meshes):
        for item in block:
            if item.users == 0:  # Check if the data block has no users
                block.remove(item)
    print("Cleaned up unused data blocks.")

def purge_unused_data():
    # Purge orphaned data blocks (run multiple times to catch dependencies)
    for _ in range(5):
        bpy.ops.outliner.orphans_purge(do_recursive=True)
    print("Purged unused data blocks.")
def start():
    # Get command line arguments after '--'
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    
    if len(argv) != 3:
        print("Usage:")
        print("blender --background --python script.py -- <source_blend> <material_name> <target_dir>")
        sys.exit(1)

    source_blend, material_name, target_dir = argv
    process_files(source_blend, material_name, target_dir)

start()