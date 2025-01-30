import bpy, bmesh
from bpy import context
from mathutils import Vector
import time

building_name = 'VAr_1_New house'

#import Terrain from blosm
def import_terrain():
    try:
        minLat = 34.072  
        maxLat = 34.2161
        minLon = 77.454
        maxLon = 77.628

        scenes = bpy.data.scenes
        
        blosm = scenes['Scene'].blosm

        blosm.minLat = float(minLat)
        blosm.maxLat = float(maxLat)
        blosm.minLon = float(minLon)
        blosm.maxLon = float(maxLon)
        
        # Calling Terrain
        blosm.dataType = 'terrain'
        bpy.ops.blosm.import_data()
    except Exception as e:
        print(e)

def cleanup():
    terrain_tiles = [obj for obj in bpy.context.scene.objects if obj.name.startswith("Terrain")]
    for terrain in terrain_tiles:
        bpy.data.objects.remove(terrain)
    
    building = bpy.data.objects[building_name]
    bpy.data.objects.remove(building)

# Bounding box helper methods
def bbox(ob):
    return (Vector(b) for b in ob.bound_box)

def bbox_axes(ob):
    bb = list(bbox(ob))
    return tuple(bb[i] for i in (0, 4, 3, 1))

def newobj(bm, original):
    me = bpy.data.meshes.new(original.name)
    bm.to_mesh(me)
    ob = bpy.data.objects.new(original.name, me)
    
    # Copy materials from the original object
    for mat in original.data.materials:
        ob.data.materials.append(mat)
        
    bpy.context.collection.objects.link(ob)
    return ob

def find_intersecting_buildings(ob, terrain_bbox_axes):
    intersecting_buildings = []
    for obj in bpy.context.scene.objects:
        if obj.name == building_name:  # Exclude terrain object
            obj_bbox = list(bbox(obj))
            if (
                obj_bbox[0].x < terrain_bbox_axes[1].x and obj_bbox[1].x > terrain_bbox_axes[0].x and
                obj_bbox[0].y < terrain_bbox_axes[2].y and obj_bbox[1].y > terrain_bbox_axes[0].y
            ):
                intersecting_buildings.append(obj)
    return intersecting_buildings

def slice_building(building, planes_x, planes_y):
    bmo = bmesh.new()
    bmo.from_mesh(building.data)
    created_objects = []

    # Create grid slices by combining X and Y planes
    for i in range(len(planes_x)-1):  # X segments
        for j in range(len(planes_y)-1):  # Y segments
            # Get current cell boundaries
            p0_x = planes_x[i]
            p1_x = planes_x[i+1]
            p0_y = planes_y[j]
            p1_y = planes_y[j+1]

            # Create working copy of the mesh
            bm = bmo.copy()

            # X-direction slicing
            bmesh.ops.bisect_plane(
                bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:],
                plane_co=(p0_x, 0, 0), plane_no=(1, 0, 0), 
                clear_inner=True
            )
            bmesh.ops.bisect_plane(
                bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:],
                plane_co=(p1_x, 0, 0), plane_no=(1, 0, 0), 
                clear_outer=True
            )

            # Y-direction slicing
            bmesh.ops.bisect_plane(
                bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:],
                plane_co=(0, p0_y, 0), plane_no=(0, 1, 0), 
                clear_inner=True
            )
            bmesh.ops.bisect_plane(
                bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:],
                plane_co=(0, p1_y, 0), plane_no=(0, 1, 0), 
                clear_outer=True
            )

            if len(bm.verts) > 0:
                new_obj = newobj(bm, building)
                created_objects.append(new_obj)

    return created_objects

def slice_terrain_and_buildings(ob):
    terrain_bbox = bbox_axes(ob)
    print("Bounding box: ", terrain_bbox)
    x_segments = 16  # 16 slices along the X axis
    y_segments = 16  # 16 slices along the Y axis

    # Ensure we are creating planes that exactly match the grid's divisions
    x_start, x_end = terrain_bbox[0].x, terrain_bbox[1].x
    y_start, y_end = terrain_bbox[0].y, terrain_bbox[2].y
    
    # Calculate the step size between each plane
    x_step = (x_end - x_start) / x_segments
    y_step = (y_end - y_start) / y_segments

    # Create the planes for slicing, including the very edge of the bounding box
    # We create intermediate planes (excluding boundaries), then add the boundaries at the start and end
    x_planes = [x_start + i * x_step for i in range(1, x_segments)]  # planes in-between, not including the edges
    y_planes = [y_start + i * y_step for i in range(1, y_segments)]  # planes in-between, not including the edges

    # Add boundary planes for the leftmost and rightmost sides (for X)
    x_planes = [x_start] + x_planes + [x_end]
    y_planes = [y_start] + y_planes + [y_end]

    # terrain_bmo = bmesh.new()
    # terrain_bmo.from_mesh(ob.data)

    # terrain_created_objects = []

    # Now create the grid of slices for terrain, ensuring both boundaries are included
    # for i in range(x_segments):  # Loop over X segments
    #     for j in range(y_segments):  # Loop over Y segments
    #         p0_x = x_planes[i]
    #         p1_x = x_planes[i + 1] if i + 1 < len(x_planes) else x_end  # Ensure we don't go out of range
    #         p0_y = y_planes[j]
    #         p1_y = y_planes[j + 1] if j + 1 < len(y_planes) else y_end  # Ensure we don't go out of range

    #         # Create a temporary copy of the terrain mesh for each slice
    #         bm = terrain_bmo.copy()

    #         # Bisect along the X direction (left-right)
    #         bmesh.ops.bisect_plane(
    #             bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
    #             plane_co=(p0_x, 0, 0), plane_no=(1, 0, 0), clear_inner=True  # X direction
    #         )

    #         bmesh.ops.bisect_plane(
    #             bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
    #             plane_co=(p1_x, 0, 0), plane_no=(1, 0, 0), clear_outer=True  # X direction
    #         )

    #         # Bisect along the Y direction (front-back)
    #         bmesh.ops.bisect_plane(
    #             bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
    #             plane_co=(0, p0_y, 0), plane_no=(0, 1, 0), clear_inner=True  # Y direction
    #         )

    #         bmesh.ops.bisect_plane(
    #             bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
    #             plane_co=(0, p1_y, 0), plane_no=(0, 1, 0), clear_outer=True  # Y direction
    #         )

    #         if len(bm.verts):  # If there are any remaining faces/verts
    #             new_obj = newobj(bm, ob)  # Create a new object for each slice
    #             terrain_created_objects.append(new_obj)

    # Slice buildings that intersect with the terrain
    intersecting_buildings = find_intersecting_buildings(ob, terrain_bbox)
    all_created_objects = []
    for building in intersecting_buildings:
        created_objects = slice_building(building, x_planes[:], y_planes[:])
        all_created_objects.extend(created_objects)
    
    # Optionally remove the original terrain object
    # bpy.data.objects.remove(ob)
    # Remove the original building object (optional, if you don't want the original)
    # bpy.data.objects.remove(building)

    return all_created_objects  # Return both terrain and building objects


import_terrain()

# Main slicing procedure
ob = bpy.data.objects["Terrain"]  # Assuming the terrain object is currently selected
slice_terrain_and_buildings(ob)
cleanup()
