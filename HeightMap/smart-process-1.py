import bpy
import numpy as np
from PIL import Image
from scipy.interpolate import griddata

# Function to normalize values to a specified range
def normalize(values, norm_range=None):
    if norm_range is None:
        min_val = np.min(values)
        max_val = np.max(values)
    else:
        min_val = norm_range['from'] if norm_range['from'] is not None else np.min(values)
        max_val = norm_range['to'] if norm_range['to'] is not None else np.max(values)
    return (values - min_val) / (max_val - min_val)

# Function to interpolate vertex data to a continuous grid
def interpolate_to_grid(vertices, resolution_x, resolution_y):
    # Extract x, y, z coordinates
    x_coords, y_coords, z_coords = vertices[:, 0], vertices[:, 1], vertices[:, 2]

    # Create a grid of the desired resolution
    grid_x, grid_y = np.meshgrid(
        np.linspace(np.min(x_coords), np.max(x_coords), resolution_x),
        np.linspace(np.min(y_coords), np.max(y_coords), resolution_y)
    )

    # Interpolate z values onto the grid
    grid_z = griddata(
        points=(x_coords, y_coords),
        values=z_coords,
        xi=(grid_x, grid_y),
        method='linear'
    )

    # Replace NaNs with zero (or a chosen fill value)
    grid_z = np.nan_to_num(grid_z, nan=0.0)

    return grid_z

# Main function to generate the height map and save it as an image
def generate_height_map(obj, resolution_x=512, resolution_y=512, normalization_method="regular", norm_range=None):
    if obj and obj.type == 'MESH':
        # Get the mesh data
        mesh = obj.data

        # Extract vertex coordinates
        vertices = np.array([[v.co.x, v.co.y, v.co.z] for v in mesh.vertices])

        # Interpolate vertex data onto a grid
        grid = interpolate_to_grid(vertices, resolution_x, resolution_y)

        # Normalize the grid based on the chosen method
        if normalization_method == "regular":
            normalized_grid = normalize(grid, norm_range)
        elif normalization_method == "smart":
            mean = np.mean(grid)
            stddev = np.std(grid)
            min_val = mean - 10 * stddev if norm_range is None or norm_range['from'] is None else norm_range['from']
            max_val = mean + 10 * stddev if norm_range is None or norm_range['to'] is None else norm_range['to']
            normalized_grid = normalize(grid, {'from': min_val, 'to': max_val})
        else:
            raise ValueError("Unknown normalization method.")

        # Scale to 0-255 for image export
        image_data = (normalized_grid * 255).astype(np.uint8)

        # Create and save a single-channel grayscale image using PIL
        img = Image.fromarray(image_data, mode="L")  # "L" mode for 8-bit grayscale

        # Flip the image along the x-axis (to correct for the mesh-to-image mapping)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # Save the height map image
        filepath = bpy.path.abspath(r"C:\Users\anubh\Downloads\Blosm\Results\vertex_height_map-interpolated.png")
        img.save(filepath)

        print(f"Height map saved at {filepath}")
    else:
        print("Please select a mesh object.")

# Call the function
obj = bpy.context.object  # Get the active object
generate_height_map(obj, resolution_x=4033, resolution_y=4033, normalization_method="smart", norm_range={'from': None, 'to': None})
