import bpy


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

    blosm.dataType = 'osm'
    # blosm.overlayType = 'osm-mapnik'
    blosm.mode = "2D"
    blosm.buildings = True
    blosm.highways = True
    blosm.water = False
    blosm.vegetation = False

    bpy.ops.blosm.import_data()  # Import data (overlay)

except Exception as e:
    print(f"Error during setup: {e}")
    # bpy.ops.wm.quit_blender()  # In case of an error, safely quit Blender