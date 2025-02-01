import bpy
import re


def restore_uvs_to_original_udim():
    # Get selected mesh objects
    selected_objects = [
        obj for obj in bpy.context.selected_objects if obj.type == "MESH"
    ]

    for obj in selected_objects:
        obj_name = obj.name
        # Find UDIM number in object name using regex
        udim_match = re.search(r"10[0-7][1-8]", obj_name)

        if not udim_match:
            print(f"No valid UDIM found in {obj_name}, skipping")
            continue

        udim_num = int(udim_match.group())
        index = udim_num - 1001

        # Validate UDIM number
        if index < 0 or index > 77:  # 1078-1001=77 is max
            print(f"Invalid UDIM {udim_num} in {obj_name}, skipping")
            continue

        U = index % 10
        V = index // 10

        # Validate grid position
        if U > 7 or V > 7:
            print(f"Invalid grid position for {udim_num}, skipping")
            continue

        # Prepare to edit UVs
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")

        if not obj.data.uv_layers.active:
            print(f"No UV layer in {obj_name}, skipping")
            continue

        uv_layer = obj.data.uv_layers.active.data

        # Restore UV coordinates
        for loop in obj.data.loops:
            uv = uv_layer[loop.index].uv
            uv.x += U
            uv.y += V

        print(f"Restored UVs for {obj_name} to UDIM {udim_num}")

    print("UV restoration complete")


restore_uvs_to_original_udim()
