import pyvista as pv
import numpy as np
import json
import msgpack
import re

# Load JSON data
data = json.load(open('context_changes_human/filtered_total_change.json', 'r'))


def format_faces_for_pyvista(faces):
    faces_formatted = np.hstack([[3, face[0], face[1], face[2]] for face in faces])
    return faces_formatted

def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)
    
annotations = load_scene_annotations()

# Loop through the data
for key in data.keys():
#     # Extract scene_id and human_id from the key

    scene_id = key  
    # if scene_id == 'None' or not scene_id.startswith('scene'):
    #     continue
    
    if scene_id != 'scene0137_00':
        continue
    # Skip if scene_id is 'None'
    
    print(f'Processing scene_id: {scene_id}')

#     Load the .npz file with the 3D scan data
    ply_file = f'3D_scans/{scene_id}/{scene_id}_filtered_vh_clean_2.npz'
    npz_data = np.load(ply_file)

    # Assuming the .npz file contains 'vertices', 'faces', and 'vertex_colors'
    vertices = npz_data['vertices']  # Replace with actual key names from the .npz file
    faces = npz_data['faces']  # Replace with actual key names from the .npz file
    colors = npz_data['vertex_colors']  # Replace with actual key names from the .npz file
    
    faces = format_faces_for_pyvista(faces)


    # Create a mesh in PyVista from vertices and faces
    mesh = pv.PolyData(vertices, faces)

    # add vertex colors to the mesh (if available)
    if colors is not None:
        mesh.point_data['colors'] = colors

    # Create a PyVista plotter for visualizing the mesh
    plotter = pv.Plotter()

    # add the mesh to the plotter
    plotter.add_mesh(mesh, scalars='colors', rgb=True)

    # add annotations as spheres and text labels
    if scene_id in annotations:
        for annotation in annotations[scene_id]:
            label = re.sub(r'<.*?>', '', annotation['text'])
            position = annotation['x'], annotation['y'], annotation['z']

            # Create a sphere for each annotation
            sphere = pv.Sphere(radius=0.02, center=position)
            plotter.add_mesh(sphere, color='red')

            # add a text label at the annotation position
            plotter.add_point_labels([position], [label], point_size=10, text_color="blue", font_size=15,always_visible=True)

    # Display the visualization
    plotter.show()
