import bpy


def move_uvs_to_udim_1001():
    # Either get selected mesh objects
    selected_objects = [
        obj for obj in bpy.context.selected_objects if obj.type == "MESH"
    ]
    # Or get all mesh objects
    # all_objects = [obj for obj in bpy.data.objects if obj.type == "MESH"]

    for obj in selected_objects:
        # Ensure we're in Object mode to edit UVs
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")

        # Check for active UV layer
        if not obj.data.uv_layers.active:
            print(f"No UV layer found for {obj.name}")
            continue

        uv_layer = obj.data.uv_layers.active.data

        # Loop through all UVs and clamp them to [0,1] by discarding integers
        for loop in obj.data.loops:
            uv = uv_layer[loop.index].uv
            uv.x = uv.x % 1.0  # Keep only the fractional part (e.g., 1.7 → 0.7)
            uv.y = uv.y % 1.0  # Same for V

    print("All UVs moved to UDIM 1001 (no scaling, only fractional parts retained).")


if __name__ == "__main__":
    move_uvs_to_udim_1001()
