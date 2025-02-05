import bpy

# List of tile objects (ensure they are in the correct order)
tiles = [obj for obj in bpy.context.scene.objects if obj.name.startswith("Terrain")]


# Sort tiles if necessary (e.g., by location or name)
# tiles.sort(key=lambda x: x.name)

# Sort tiles based on their location:
# - First, sort by Y (vertical) in ascending order (bottom to top).
# - Then, sort by X (horizontal) in ascending order (left to right).
tiles.sort(key=lambda x: (x.location.y, x.location.x))

# Rename tiles based on UDIM numbering (vertical-first order)
udim_start = 1001
columns = 8
rows = 8

for row in range(rows):
    for col in range(columns):
        index = (columns - 1 - col) * rows + (rows - 1 - row)
        # index = col * rows + row  # Verticle Division
        # index = row * columns + col  # Horizontal Division

        if index < len(tiles):
            # udim_number = udim_start + col + row * 10
            # udim_number = udim_start + col + (rows - 1 - row) * 10
            # udim_number = udim_start + (columns - 1 - col) + row * 10
            udim_number = udim_start + row * 10 + col
            print(row, col, index, udim_number)
            tiles[index].name = f"Terrain_{udim_number}"
            tiles[
                index
            ].data.name = f"Terrain_{udim_number}"  # Rename the mesh data as well

print("Renaming complete!")

"""
For BL-TR
tiles.sort(key=lambda x: (x.location.y, x.location.x))
index = row * columns + col # Horizontal Division
udim_number = udim_start + col + (rows - 1 - row) * 10


For BR-TL
tiles.sort(key=lambda x: (x.location.y, x.location.x))
index = (columns - 1 - col) * rows + (rows - 1 - row)
udim_number = udim_start + row * 10 + col
"""
