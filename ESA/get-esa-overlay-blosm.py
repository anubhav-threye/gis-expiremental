import bpy
import sys

try:
    minLat = sys.argv[-4]
    maxLat = sys.argv[-3]
    minLon = sys.argv[-2]
    maxLon = sys.argv[-1]

    scenes = bpy.data.scenes
    
    blosm = scenes['Scene'].blosm

    blosm.minLat = float(minLat)
    blosm.maxLat = float(maxLat)
    blosm.minLon = float(minLon)
    blosm.maxLon = float(maxLon)

    # Adding Overlay
    blosm.dataType = 'overlay'
    blosm.overlayType = 'esa-local'
    blosm.saveOverlayToFile = True
    
    bpy.ops.blosm.import_data()
except Exception as e:
    print(e)
    sys.exit(1)