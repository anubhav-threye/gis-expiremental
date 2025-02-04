import bpy

# Define the 8x8 terrain grid as 4 quadrants (each 4x4)
quadrants = {
    1: {"start_udim": 1001, "uv_offset": (0, 0)},  # Q1 (Bottom-Left)
    2: {"start_udim": 1041, "uv_offset": (0, 4)},  # Q2 (Top-Left)
    3: {"start_udim": 1005, "uv_offset": (4, 0)},  # Q3 (Bottom-Right)
    4: {"start_udim": 1045, "uv_offset": (4, 4)},  # Q4 (Top-Right)
}

# Dictionary to store the mapping
udim_mapping = {}

def get_udim_name(quadrant, tile_index):
    # Iterate through each quadrant
    start_udim = quadrants[quadrant]["start_udim"]
    u_offset, v_offset = quadrants[quadrant]["uv_offset"]

    # Iterate through 4x4 tiles within each quadrant
    # for tile_index in range(16):  # 1-16 in each quadrant
    row = tile_index // 4  # Y position (0-3)
    col = tile_index % 4  # X position (0-3)

    # Calculate final UDIM position
    u = u_offset + col
    v = v_offset + row
    udim = 1001 + u + (v * 10)

    # Tile name format: Quadrant-TileNumber (e.g., "1-1", "2-3")
    tile_name = f"{quadrant}-{tile_index + 1}"
    udim_mapping[tile_name] = udim

    return str(udim)


# Iterate through all objects in the scene
for obj in bpy.context.scene.objects:
    if "-" in obj.name:  # Check if the object follows the naming convention
        try:
            # Split the name into quadrant and tile number
            quadrant, tile_number = obj.name.split("-")
            quadrant = int(quadrant)
            tile_number = int(tile_number) - 1

            # Calculate the UDIM name
            udim_name = get_udim_name(quadrant, tile_number)

            # Rename the object
            obj.name = udim_name
            obj.data.name = udim_name  # Rename the mesh data as well
        except ValueError:
            print(f"Skipping object {obj.name} due to invalid naming format.")

# Print the mapping
for tile, udim in udim_mapping.items():
    print(f"{tile} -> UDIM {udim}")
