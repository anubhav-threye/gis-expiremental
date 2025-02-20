# WIP: Unchecked Script - Not Working, supposed-bly

import bpy
import json
import mathutils

EXPORT_PATH = r"E:\Projects\GIS\GIS-WSL\gis-expiremental\data\3d_tiles"


def get_tile_bounds(obj):
    """Get the bounding box of a Blender object in world coordinates"""
    bbox_corners = [
        obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box
    ]
    min_x = min(v.x for v in bbox_corners)
    min_y = min(v.y for v in bbox_corners)
    min_z = min(v.z for v in bbox_corners)
    max_x = max(v.x for v in bbox_corners)
    max_y = max(v.y for v in bbox_corners)
    max_z = max(v.z for v in bbox_corners)

    return {"min": [min_x, min_y, min_z], "max": [max_x, max_y, max_z]}


def get_transform_matrix(obj):
    """Get the transformation matrix as a 4x4 row-major array"""
    matrix = obj.matrix_world.transposed()  # Convert to row-major order for JSON
    return [val for row in matrix for val in row]


def generate_tileset():
    """Generate tileset.json for the terrain tiles in Blender"""
    tiles = []

    for obj in bpy.context.selected_objects:
        if (
            obj.type == "MESH" and "Tile" in obj.name
        ):  # Modify naming convention if needed
            tile_data = {
                "boundingVolume": {"box": get_tile_bounds(obj)},
                "transform": get_transform_matrix(obj),
                "geometricError": 1.0,  # Adjust based on LOD
                "content": {
                    "uri": f"{obj.name}.glb"  # Reference to the 3D model file
                },
            }
            tiles.append(tile_data)

    tileset = {
        "asset": {"version": "1.0"},
        "geometricError": 10.0,
        "root": {
            "boundingVolume": {
                "box": get_tile_bounds(
                    bpy.context.scene.objects[0]
                )  # Root bounding box
            },
            "transform": get_transform_matrix(bpy.context.scene.objects[0]),
            "geometricError": 10.0,
            "refine": "ADD",
            "children": tiles,
        },
    }

    # Save to tileset.json
    with open(f"{EXPORT_PATH}/tileset.json", "w") as f:
        json.dump(tileset, f, indent=4)

    print("tileset.json generated successfully.")


# Run the script
generate_tileset()
