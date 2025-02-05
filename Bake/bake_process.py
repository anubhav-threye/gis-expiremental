import bpy
import re
import os


# -------------------------------------------
# General Scene Settings
# -------------------------------------------
def scene_setup():
    """
    Sets up the scene for a diffuse bake.

    This function sets the render engine to Cycles,
    the device to GPU,
    the bake type to diffuse,
    and configures the bake passes.
    """
    scene = bpy.context.scene
    # Render Settings
    scene.render.engine = "CYCLES"  # Render Engine

    cycles = scene.cycles  # Get Cycles
    render = scene.render  # Get Render
    view = scene.view_settings  # Get View Settings
    display = scene.display_settings  # Get Display Settings

    cycles.device = "GPU"  # Device -> GPU Compute

    # ------------- SAMPLING -------------
    # Viewport Sampling
    cycles.preview_adaptive_threshold = 0.1  # Noise Threshold
    cycles.preview_samples = 25  # Max Samples
    cycles.preview_adaptive_min_samples = 0  # Min Samples
    cycles.use_preview_denoising = False  # Denoising

    # Render Sampling
    cycles.adaptive_threshold = 0.01  # Noise Threshold
    cycles.samples = 5  # Max Samples
    cycles.adaptive_min_samples = 0  # Min Samples
    cycles.time_limit = 0  # Time Limit
    cycles.use_denoising = False  # Denoising

    # ------------- LIGHT PATHS -------------
    # Max Bounces
    cycles.max_bounces = 12  # Total
    cycles.diffuse_bounces = 4  # Diffuse
    cycles.glossy_bounces = 4  # Glossy
    cycles.transmission_bounces = 12  # Transmission
    cycles.volume_bounces = 0  # Volume
    cycles.transparent_max_bounces = 8  # Transparent

    # Clamping
    cycles.sample_clamp_direct = 0.0  # Direct Light
    cycles.sample_clamp_indirect = 10.0  # Indirect Light

    # Caustics
    cycles.blur_glossy = 1.0  # Filter Glossy
    cycles.caustics_reflective = False  # Caustics Reflective
    cycles.caustics_refractive = False  # Caustics Refractive
    cycles.use_fast_gi = False  # Fast GI Approximation

    # ------------- SIMPLIFY -------------
    # Viewport Simplify
    render.use_simplify = True  # Simplify ON
    render.simplify_subdivision = 6  # Max Subdivision
    render.simplify_child_particles = 1  # Child Particles
    cycles.texture_limit = "512"  # Texture Limit
    render.simplify_volumes = 1.0  # Volume Resolution
    render.use_simplify_normals = False  # Normals

    # Render Simplify
    render.simplify_subdivision_render = 6  # Max Subdivision
    render.simplify_child_particles_render = 1  # Child Particles
    cycles.texture_limit_render = "OFF"  # Texture Limit
    render.simplify_gpencil = False  # Grease Pencil

    # ------------- COLOR MANAGEMENT -------------
    display.display_device = "sRGB"  # Display Device
    view.view_transform = "Filmic"  # View Transform
    view.look = "Very High Contrast"  # Look
    view.exposure = 1.0  # Exposure
    view.gamma = 1.0  # Gamma
    scene.sequencer_colorspace_settings.name = "sRGB"  # Sequencer
    view.use_curve_mapping = False  # Use Curve


def bake_settings(bake_type="DIFFUSE"):
    scene = bpy.context.scene

    cycles = scene.cycles  # Get Cycles
    bake = scene.render.bake  # Get Bake

    # ------------- Bake Settings -------------
    cycles.bake_type = bake_type  # Bake Type

    # Contributions
    bake.use_pass_direct = False  # Direct
    bake.use_pass_color = True  # Color
    bake.use_pass_indirect = False  # Indirect
    bake.use_selected_to_active = False  # Selective To Active

    # Output
    bake.target = "IMAGE_TEXTURES"  # Target
    bake.use_clear = True  # Clear Image

    # Margin
    bake.margin_type = "ADJACENT_FACES"  # Type
    bake.margin = 0  # Size


# -------------------------------------------
# Bake Process
# -------------------------------------------
# GLOBAL CONSTANTS
PREFIX = "Q4"
RESOLUTION = 1024
COLOR = (0.0, 0.0, 0.0, 1.0)  # Black with full alpha
OUT_PATH = r"E:\Projects\GIS\GIS-WSL\gis-expiremental\data\Bake"
BAKE_TYPES = {"DIFFUSE": "Diffuse", "NORMAL": "Normal", "ROUGHNESS": "Roughness"}

# GLOBAL VARIABLES
nodes_list = []


def fill_tile(image, image_name):
    # Manually find an area that supports the Image Editor
    override = None
    for area in bpy.context.window_manager.windows[0].screen.areas:
        if area.type == "IMAGE_EDITOR":
            override = {
                "area": area,
                "region": area.regions[0],
                "space_data": area.spaces.active,
            }
            break

    if override:
        with bpy.context.temp_override(**override):
            bpy.context.space_data.image = image
            # Rather than getting the last index to set the active tile, we get the image via name and set it to 1
            bpy.data.images[image_name].tiles.active_index = 1
            bpy.ops.image.tile_fill(color=COLOR, width=RESOLUTION, height=RESOLUTION)
            print(f"Filled -> {image_name}")

            # Remove other tiles from the image
            # image.tiles.remove(image.tiles[0])
            for tile in image.tiles:
                # Tile is of UDIMTiles struct [https://docs.blender.org/api/current/bpy.types.UDIMTiles.html]
                if tile.number == 1001:
                    print("Deleted 1001")
                    image.tiles.remove(tile)
    else:
        print("Unable to override image editor context")


def create_image_tile(udim_name, texture_node, bake_suffix):
    # Create a new blank image
    image_name = f"{bake_suffix}_{udim_name}"
    image = bpy.data.images.new(
        name=image_name,
        width=RESOLUTION,
        height=RESOLUTION,
        alpha=False,
        float_buffer=False,
        tiled=True,
    )
    image.seam_margin = 0
    try:
        # Link the image to texture image node
        texture_node.image = image

        if udim_name == "1001":
            return image

        tile_number = int(udim_name)
        image.tiles.new(tile_number=tile_number)

        # Fill the tile
        fill_tile(image, image_name)

        return image
    except ValueError:
        print(f"Invalid UDIM tile number: {udim_name}. Skipping object.")

        return None


def setup_material_nodes(material):
    nodes = material.node_tree.nodes
    _links = material.node_tree.links

    # Create temporary nodes for baking
    texture_node = nodes.new("ShaderNodeTexImage")
    nodes.active = texture_node

    return texture_node, None


def create_image_texture(obj, udim_name):
    # Ensure object has material
    if not obj.data.materials:
        print(f"No material found on {obj.name}. Please add one and run again.")
        return

    material = obj.data.materials[0]
    # Ensure material uses nodes
    material.use_nodes = True

    for bake_type, bake_suffix in BAKE_TYPES.items():
        # Setup nodes for current bake type
        texture_node, normal_node = setup_material_nodes(material)
        nodes_list.append(texture_node)
        if normal_node:
            nodes_list.append(normal_node)

        # Create image and bake
        image = create_image_tile(udim_name, texture_node, bake_suffix)

        if image:
            bake_settings(bake_type)
            init_bake(image, bake_type, bake_suffix, udim_name)

        # Cleanup nodes
        if normal_node:
            material.node_tree.nodes.remove(normal_node)
        material.node_tree.nodes.remove(texture_node)

    # Purge unused data blocks
    bpy.ops.outliner.orphans_purge(do_recursive=True)


def init_bake(image, bake_type, bake_suffix, udim_name):
    if not image:
        print("No Image found to bake")
        return

    try:
        print(f"Baking: {udim_name} -> {bake_suffix}...")
        bpy.context.scene.render.bake.use_selected_to_active = False
        bpy.ops.object.bake(
            type=bake_type,
            pass_filter={"COLOR"},
            width=RESOLUTION,
            height=RESOLUTION,
            margin=0,
            margin_type="ADJACENT_FACES",
            use_clear=True,
        )
        export_texture(image, bake_suffix, udim_name)
    finally:
        # Cleanup memory
        if image.users == 0:
            bpy.data.images.remove(image)


def export_texture(image, bake_suffix, udim_name):
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)

    file_name = f"{PREFIX}_{bake_suffix}_<UDIM>.jpg"
    file_path = os.path.join(OUT_PATH, file_name)

    # Save settings
    image.filepath_raw = file_path
    image.file_format = "JPEG"
    image.save()
    print(f"Exported: {file_path}")


def start(obj):
    for obj in bpy.context.selected_objects:
        match = re.match(r"(\d+)_(\d{4})", obj.name)
        if match:
            udim = match.group(2)
            create_image_texture(obj, udim)
        else:
            print(f"Skipping {obj.name} - invalid format")


def main():
    # Deselect all the objects
    bpy.ops.object.select_all(action="DESELECT")

    # Set up the scene
    scene_setup()

    # Iterate over all the objects in the scene
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue

        # Select the object
        obj.select_set(True)

        # Call the start function
        start(obj)

        # Deselect the object
        obj.select_set(False)


# Initialize
main()
