import bpy

quadrant_config = {
    1: {
        "base": 1001,
        "prefix": "Q1_",
        "grid_pos": (0, 0),
    },  # Bottom-left after rotation
    2: {"base": 1041, "prefix": "Q2_", "grid_pos": (0, 4)},  # Top-left after rotation
    3: {
        "base": 1005,
        "prefix": "Q3_",
        "grid_pos": (4, 0),
    },  # Bottom-right after rotation
    4: {"base": 1045, "prefix": "Q4_", "grid_pos": (4, 4)},  # Top-right after rotation
}


def get_quadrant(udim_num):
    for q in quadrant_config.values():
        base = q["base"]
        if base <= udim_num < base + 40:  # 4x10 grid check
            offset = udim_num - base
            if offset % 10 < 4 and offset // 10 < 4:
                return q
    return None


def calculate_split_udim(original_udim, suffix, quadrant):
    # Calculate base position in quadrant
    offset = original_udim - quadrant["base"]
    local_x = offset % 10  # 0-3
    local_y = offset // 10  # 0-3

    # Rotate 90 degrees clockwise to get original position
    orig_u = 3 - local_y  # Original X becomes rotated Y
    orig_v = local_x  # Original Y becomes rotated X

    # Calculate split component positions
    suffix_map = {
        "": (0, 1),  # Top-left
        ".001": (1, 1),  # Top-right
        ".002": (1, 0),  # Bottom-right
        ".003": (0, 0),  # Bottom-left
    }

    du, dv = suffix_map.get(suffix, (None, None))
    if du is None:
        return None

    # Apply quadrant grid offset
    grid_u, grid_v = quadrant["grid_pos"]
    final_u = grid_u + orig_u * 2 + du
    final_v = grid_v + orig_v * 2 + dv

    # Calculate final UDIM
    return 1001 + final_u + final_v * 10


# Main processing
for obj in bpy.context.scene.objects:
    if obj.type != "MESH" or not obj.name.isdigit():
        continue

    udim_num = int(obj.name)
    quadrant = get_quadrant(udim_num)
    if not quadrant:
        continue

    # Store original name and prepare for separation
    original_name = obj.name
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Separate mesh
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")

    # Rename separated parts
    for o in bpy.context.selected_objects:
        if not o.name.startswith(original_name):
            continue

        suffix = o.name[len(original_name) :]
        new_udim = calculate_split_udim(udim_num, suffix, quadrant)

        if new_udim:
            new_name = f"{quadrant['prefix']}{new_udim}"
            o.name = o.data.name = new_name

    # Cleanup
    bpy.ops.object.select_all(action="DESELECT")

print("All quadrants processed correctly!")
