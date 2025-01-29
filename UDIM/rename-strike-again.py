import bpy

# Define the 8x8 terrain grid as 4 quadrants (each 4x4)
quadrants = {
    1: {"uv_offset": (0, 0)},  # Q1 (Original Bottom-Left)
    2: {"uv_offset": (0, 4)},  # Q2 (Original Top-Left)
    3: {"uv_offset": (4, 0)},  # Q3 (Original Bottom-Right)
    4: {"uv_offset": (4, 4)},  # Q4 (Original Top-Right)
}

# Dictionary to store the mapping
udim_mapping = {}


def get_udim_name(quadrant, tile_index):
    uv_offset = quadrants[quadrant]["uv_offset"]
    u_offset, v_offset = uv_offset

    # Calculate original grid position within quadrant
    row = tile_index // 4  # 0-3
    col = tile_index % 4  # 0-3

    # Original UV coordinates before rotation
    original_u = u_offset + col
    original_v = v_offset + row

    # Apply 90-degree clockwise rotation to entire grid
    new_u = original_v
    new_v = 7 - original_u

    # Calculate final UDIM
    udim = 1001 + new_u + (new_v * 10)

    # Store mapping
    tile_name = f"{quadrant}-{tile_index + 1}"
    udim_mapping[tile_name] = udim

    return str(udim)


# Iterate through all objects in the scene
for obj in bpy.context.scene.objects:
    if "-" in obj.name:
        try:
            quadrant, tile_number = obj.name.split("-")
            quadrant = int(quadrant)
            tile_number = int(tile_number) - 1  # Convert to 0-based index

            udim_name = get_udim_name(quadrant, tile_number)

            # Rename object and mesh data
            obj.name = udim_name
            obj.data.name = udim_name
        except ValueError:
            print(f"Skipping object {obj.name} due to invalid format")

# Print mapping for verification
print("\nUDIM Mapping:")
for tile, udim in sorted(udim_mapping.items()):
    print(f"{tile.ljust(6)} → UDIM {udim}")
