import bpy
import time

# Flip Terrain on Z-scale
bpy.data.objects["Terrain"].scale[2] = -1

def get_collection_by_name(collection_name):
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
        print(f"Collection '{collection_name}' found: {collection}")
        return collection
    else:
        print(f"Collection '{collection_name}' not found.")
        return None

   
def simulate_drop_it(obj):
    if not obj:
        print("No object provided to simulate Drop It.")
        return

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Create an override context for the 3D Viewport
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            with bpy.context.temp_override(area=area):
                try:
                    # Call the 'DROP IT' operator
                    bpy.ops.object.drop_it(drop_by='lw_vertex', offset_z=0.1)
                    print(f"'Drop It' applied to: {obj.name}")
                except RuntimeError as e:
                    print(f"Failed to apply 'Drop It' to {obj.name}: {e}")
            break
    else:
        print("No VIEW_3D area found in the current context.")


    
    
def hide_all_meshes(objects):
    for obj in objects:
        if obj.type == 'MESH':
            obj.hide_set(True)


def process_view(collection_name):
    # Get the Collection
    osm_buildings_collection = get_collection_by_name(collection_name)
    
    if not osm_buildings_collection:
        return
    
    if osm_buildings_collection:    
        # Get all mesh objects in the scene
        mesh_objects = [obj for obj in osm_buildings_collection.objects if obj.type == 'MESH']
        
        # Hide all meshes
        hide_all_meshes(osm_buildings_collection.objects)
    
        for obj in mesh_objects:
            # Show the mesh
            obj.hide_set(False)
            simulate_drop_it(obj)
    
            time.sleep(0.5)
    
            # Hide the mesh again
            obj.hide_set(True)
            
            
# Run the function
collection_name = "map.osm_buildings"
process_view(collection_name)
