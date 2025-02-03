import bpy
from mathutils import Vector


def merge_tiles(source_z, target_z):
    ratio = 2 ** (source_z - target_z)
    tiles = [obj for obj in bpy.data.objects if obj.type == "MESH"]

    for x in range(0, 2**target_z):
        for y in range(0, 2**target_z):
            # Find child tiles
            children = []
            for dx in range(ratio):
                for dy in range(ratio):
                    child = next(
                        (
                            t
                            for t in tiles
                            if f"tile_{x * ratio + dx}_{y * ratio + dy}_{source_z}"
                            in t.name
                        ),
                        None,
                    )
                    if child:
                        children.append(child)

            # Merge meshes
            bpy.ops.object.select_all(action="DESELECT")
            for child in children:
                child.select_set(True)
            bpy.context.view_layer.objects.active = children[0]
            bpy.ops.object.join()

            # Rename and set origin
            merged = bpy.context.active_object
            merged.name = f"tile_{x}_{y}_{target_z}"
            merged.location = Vector((0, 0, 0))

            # Add custom properties
            merged["children"] = [c.name for c in children]


def weld_vertices():
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.remove_doubles(threshold=0.01)
    bpy.ops.object.mode_set(mode="OBJECT")


def export_level(z):
    base_path = r"E:\Projects\GIS\GIS-WSL\gis-expiremental\data\terrain tiles to decimate\16-tiles"

    tiles = [obj for obj in bpy.data.objects if obj.name.startswith(f"tile_")]
    for t in tiles:
        if f"_{z}" in t.name:
            t.select_set(True)
    bpy.ops.export_scene.glb(
        filepath=f"{base_path}\tiles_z{z}.glb",
        selected=True,
    )


# Usage:
merge_tiles(3, 2)  # 64 -> 16 tiles
# merge_tiles(2, 1)  # 16 -> 4 tiles
# merge_tiles(1, 0)  # 4 -> 1 tile

weld_vertices()
export_level()
