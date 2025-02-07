import bpy
import sys
from time import sleep

try:
    min_lat, max_lat = 34.07201, 34.21606
    min_lon, max_lon = 77.45396, 77.62802
    
    # minLat = sys.argv[-4]
    # maxLat = sys.argv[-3]
    # minLon = sys.argv[-2]
    # maxLon = sys.argv[-1]

    scenes = bpy.data.scenes
    
    blosm = scenes['Scene'].blosm
    
    # print("blosm-premium-mod" in bpy.context.preferences.addons)
    # blosm = "blosm-premium-mod" in bpy.context.preferences.addons and sys.modules.get("blosm-premium-mod")

    blosm.minLat = float(min_lat)
    blosm.maxLat = float(max_lat)
    blosm.minLon = float(min_lon)
    blosm.maxLon = float(max_lon)
    
    # Calling Terrain
    blosm.dataType = 'terrain'
    bpy.ops.blosm.import_data()
except Exception as e:
    print(e)