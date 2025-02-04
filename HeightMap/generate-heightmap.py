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

# Main function to generate the height map and save it as an image
def generate_height_map(
    obj,
    resolution_x=512,
    resolution_y=512,
    normalization_method="regular",
    norm_range=None,
    output_dir="C://",
):
    # Apply All Transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    if obj and obj.type == 'MESH':
        # Get the mesh data
        mesh = obj.data

        # Extract vertex coordinates
        vertices = np.array([[v.co.x, v.co.y, v.co.z] for v in mesh.vertices])
        x_coords, y_coords, z_coords = vertices[:, 0], vertices[:, 1], vertices[:, 2]

        # Create a grid of the desired resolution
        grid_x, grid_y = np.meshgrid(
            np.linspace(np.min(x_coords), np.max(x_coords), resolution_x),
            np.linspace(np.min(y_coords), np.max(y_coords), resolution_y)
        )

        # Interpolate vertex data onto the grid
        grid_z = griddata((x_coords, y_coords), z_coords, (grid_x, grid_y), method='linear')

        # Replace NaN values with the minimum value in the grid
        grid_z = np.nan_to_num(grid_z, nan=np.min(z_coords))

        # Normalize the grid based on the chosen method
        if normalization_method == "regular":
            normalized_grid = normalize(grid_z, norm_range)
        elif normalization_method == "smart":
            mean = np.mean(grid_z)
            stddev = np.std(grid_z)
            actual_max = np.max(grid_z)
            actual_min = np.min(grid_z)
            numStdDeviations = 10
            min_val = max(mean - numStdDeviations * stddev, actual_min) if norm_range is None or norm_range['from'] is None else norm_range['from']
            max_val = min(mean + numStdDeviations * stddev, actual_max) if norm_range is None or norm_range['to'] is None else norm_range['to']
            
            normalized_grid = normalize(grid_z, {'from': min_val, 'to': max_val})
        else:
            raise ValueError("Unknown normalization method.")

        # Note: For 8-bit image export -> Scale to 0-255 -> Convert to uint8 -> Mode "L" for 8-bit grayscale
        # Scale to 0-65535 for image export
        image_data = (normalized_grid * 65535).astype(np.uint16)

        # Create and save a single-channel grayscale image using PIL
        img = Image.fromarray(image_data, mode="I;16")  # "I;16" mode for 16-bit grayscale

        # Flip the image along the x-axis (to correct for the mesh-to-image mapping)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # Save the height map image
        filepath = bpy.path.abspath(
            rf"{output_dir}\vertex_height_map-interpolated-smarty-16bit.png"
        )
        img.save(filepath)

        print(f"Height map saved at {filepath}")
    else:
        print("Please select a mesh object.")

# Call the function
obj = bpy.context.object  # Get the active object
output_dir = "E:\Projects\GIS\Blosm-HeightMap\Results"

generate_height_map(
    obj,
    resolution_x=4096,
    resolution_y=4096,
    normalization_method="regular",
    norm_range={"from": None, "to": None},
    output_dir=output_dir,
)
