import bpy
import sys
from time import sleep
import threading

# Create an event to track the thread
thread_event = threading.Event()

def print_scene_objects():
    try:
        trigger = True
        while trigger:
            # sleep(1)
            for object in bpy.context.scene.objects:
                print(object.name)
                if object.name == 'Cube':
                    pass
                
                if object.name == 'Terrain':
                    for material in object.material_slots:
                        print('\t' + material.name)
                        if material.name:
                            trigger = False
    finally:
        thread_event.set()
        
    


try:
    minLat = 34.072  
    maxLat = 34.2161
    minLon = 77.454
    maxLon = 77.628
    
    # minLat = sys.argv[-4]
    # maxLat = sys.argv[-3]
    # minLon = sys.argv[-2]
    # maxLon = sys.argv[-1]

    scenes = bpy.data.scenes
    
    blosm = scenes['Scene'].blosm
    
    # print("blosm-premium-mod" in bpy.context.preferences.addons)
    # blosm = "blosm-premium-mod" in bpy.context.preferences.addons and sys.modules.get("blosm-premium-mod")

    blosm.minLat = float(minLat)
    blosm.maxLat = float(maxLat)
    blosm.minLon = float(minLon)
    blosm.maxLon = float(maxLon)
    
    # Calling Terrain
    blosm.dataType = 'terrain'
    # bpy.ops.blosm.import_data()

    # Adding Overlay
    blosm.dataType = 'overlay'
    blosm.overlayType = 'esa-local'
    blosm.saveOverlayToFile = True

    bpy.ops.blosm.import_data()
    
    # Create and start a new thread
    thread = threading.Thread(target=print_scene_objects)
    thread.start()
    
    # Wait for the thread to complete
    # thread_event.wait()
    # sys.exit(0)

    # glb_path = r"E:\Projects\GIS\GIS-WSL\Research & Experimental\notebook\generated_glb\1.glb"
    # bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB')
except Exception as e:
    print(e)
    # sys.exit(1)