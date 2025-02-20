import bpy, math, json
from mathutils import Matrix, Vector

EXPORT_PATH = r"E:\Projects\GIS\GIS-WSL\gis-expiremental\data\3d_tiles"

# Define the total geographic extent (in degrees)
min_lat = 34.07201  # replace with your actual min latitude
max_lat = 34.21606  # replace with your actual max latitude
min_lon = 77.45396  # replace with your actual min longitude
max_lon = 77.62802  # replace with your actual max longitude

num_rows = 16
num_cols = 16


def geographic_to_blender(lon, lat):
    """
    Converts geographic coordinates (lon, lat) in degrees to local Blender coordinates.
    This simple approximation uses a reference at (min_lon, min_lat) and scales degrees to meters.
    """
    # Approximate meters per degree (latitude)
    meters_per_degree_lat = 111320
    # For longitude, adjust by the cosine of the latitude (approximation)
    meters_per_degree_lon = 111320 * math.cos(math.radians(lat))

    # Compute offsets relative to the reference (min_lon, min_lat)
    x = (lon - min_lon) * meters_per_degree_lon
    y = (lat - min_lat) * meters_per_degree_lat
    # Assuming Z=0 for terrain elevation here; adjust if your terrain includes vertical offset.
    return Vector((x, y, 0))


tiles_data = []  # This will store info for each tile

for i in range(num_rows):
    for j in range(num_cols):
        # Compute tile extents in geographic degrees.
        tile_lat_min = min_lat + i * (max_lat - min_lat) / num_rows
        tile_lat_max = min_lat + (i + 1) * (max_lat - min_lat) / num_rows
        tile_lon_min = min_lon + j * (max_lon - min_lon) / num_cols
        tile_lon_max = min_lon + (j + 1) * (max_lon - min_lon) / num_cols

        # Calculate the geographic center of the tile.
        center_lat = (tile_lat_min + tile_lat_max) / 2.0
        center_lon = (tile_lon_min + tile_lon_max) / 2.0

        # Convert the center to Blender's local coordinates.
        translation = geographic_to_blender(center_lon, center_lat)

        # Create a 4x4 translation matrix from the computed translation vector.
        transform_matrix = Matrix.Translation(translation)

        # Convert the matrix into a list-of-lists (row-major order)
        matrix_list = [list(row) for row in transform_matrix]

        # For a Cesium region bounding volume, the values are:
        # [west, south, east, north, minHeight, maxHeight]
        # Here, we convert degrees to radians and set min/max height to 0.
        region = [
            math.radians(tile_lon_min),  # west
            math.radians(tile_lat_min),  # south
            math.radians(tile_lon_max),  # east
            math.radians(tile_lat_max),  # north
            0,  # minHeight (adjust if needed)
            0,  # maxHeight (adjust if needed)
        ]

        # Store the tile’s information (this can be expanded as needed)
        tile_info = {
            "row": i,
            "col": j,
            "transform_matrix": matrix_list,
            "region": region,
        }
        tiles_data.append(tile_info)

# Write the tiles data to a JSON file (for debugging or later integration)
with open(f"{EXPORT_PATH}\tiles_data.json", "w") as f:
    json.dump(tiles_data, f, indent=4)
