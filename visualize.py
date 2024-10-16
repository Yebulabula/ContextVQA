import pyvista as pv
import numpy as np
import json
import msgpack
import re

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)
    
scene_annotations = load_scene_annotations()

def format_faces_for_pyvista(faces):
    # Each face needs to start with the number of vertices (3 for triangles)
    num_faces = faces.shape[0]
    # Create an array where each triangle face is prefixed by the number 3 (for triangles)
    faces_formatted = np.hstack([[3, face[0], face[1], face[2]] for face in faces])
    return faces_formatted


data = load_json('context_changes_human/category_non_similar_filtered_total_change.json')

for scene_id in data:
    if scene_id > 'scene0300_00':
        # Load the .npz file containing mesh data
        ply_file = f'3D_scans/{scene_id}/{scene_id}_filtered_vh_clean_2.npz'
        npz_data = np.load(ply_file)
        print(f'Processing scene: {scene_id}')
        # Extract vertices, faces, and colors from the .npz file
        vertices = npz_data['vertices']  # Replace with actual key names from the .npz file
        faces = npz_data['faces']  # Replace with actual key names from the .npz file
        colors = npz_data['vertex_colors']  # Replace with actual key names from the .npz file
        
        # Format faces to be compatible with PyVista
        faces = format_faces_for_pyvista(faces)

        # Create a mesh object
        mesh = pv.PolyData(vertices, faces)

        # Add vertex colors to the mesh (if available)
        if colors is not None:
            mesh.point_data['colors'] = colors  # Normalize if colors are in the 0-255 range

        # Create a PyVista plotter for visualizing the mesh
        plotter = pv.Plotter()

        # Add the mesh to the plotter and specify colors
        plotter.add_mesh(mesh, scalars='colors', rgb=True)

        # Get annotations for the current scene
        annotations = scene_annotations[scene_id]

        # Add annotations (labels) to the plotter
        for annotation in annotations:
            position = (annotation['x'], annotation['y'], annotation['z'])  # Extract the 3D position of the annotation
            # extract from <b>couch</b> to couch
            label = re.sub('<[^<]+?>', '', annotation['text'])
            font_opts = {
                'font_size': 12,
                'point_color': 'white',
                'always_visible': True
            }
            # Add the point label with the text annotation
            plotter.add_point_labels([position], [label], **font_opts)

        # Show the plotter  
        plotter.show()
