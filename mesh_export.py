import json
import bpy
import bmesh
import pprint
import pathlib

def delete_all_objects():
    """Remove all objects from the scene"""
    if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.mode_set(mode="OBJECT")
        
        bpy.ops.object.select_all(action="SELECT")
        
    bpy.ops.object.delete()
    


def get_mesh_data(obj):

    area = next((a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'), None)
    if not area:
        raise RuntimeError("Open a 3D Viewport!")
    override = bpy.context.copy()
    override['area'] = area
    override['region'] = area.regions[-1]
    override['active_object'] = obj
    
    with bpy.context.temp_override(**override):
        bpy.ops.object.mode_set(mode='EDIT')
    
    bm = bmesh.from_edit_mesh(obj.data)
    
    face_to_vert = [[v.index for v in f.verts] for f in bm.faces]
    vert_coords = [None] * len(bm.verts)
    for v in bm.verts:
        world_co = obj.matrix_world @ v.co
        vert_coords[v.index] = [round(c, 6) for c in world_co]
    
    with bpy.context.temp_override(**override):
        bpy.ops.object.mode_set(mode='OBJECT')
    
    data = {
        "object_name": obj.name,
        "face_verts": face_to_vert,
        "vert_coordinates": vert_coords,
    }
    pprint.pprint(data)
    return data

def get_path_to_mesh_data():
    return pathlib.Path.home() / "tmp" / "mesh.json"


def save_data(data):
    path_to_file = get_path_to_mesh_data()

    path_to_file.parent.mkdir(parents=True, exist_ok=True)

#open json file for writing and dump into text form
    with open(path_to_file, "w") as out_file_obj:
        text = json.dumps(data, indent=4)
        out_file_obj.write(text)

def create_json_data_from_mesh():   
    
    obj = bpy.context.view_layer.objects.active
    if not obj or obj.type != 'MESH':
        selected = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        if not selected:
            raise ValueError("Please select a MESH object first!")
        obj = selected[0]                     #use first selected mesh
    
    print(f"Exporting: {obj.name}")
    data = get_mesh_data(obj)                 
    save_data(data)
    
    
def load_data():
    path_to_file = get_path_to_mesh_data()
    with open(path_to_file, "r") as in_file_obj:
        text = in_file_obj.read()
        data = json.loads(text)
    return data

def create_mesh_from_data(data):
    verts = data["vert_coordinates"]
    faces = data["face_verts"]
    edges = []
    
    object_name = data["object_name"]
    
    mesh_data = bpy.data.meshes.new(f"{object_name}_data")
    mesh_data.from_pydata(verts, edges, faces)
    
    mesh_obj = bpy.data.objects.new(object_name, mesh_data)
    bpy.context.collection.objects.link(mesh_obj)




def create_mesh_from_json_data():
    data = load_data()
    
    create_mesh_from_data(data)


def main():
    create_json_data_from_mesh()
    create_mesh_from_json_data()

main()
