import pyvista as pv
import numpy as np
import json
import msgpack
import re

# Load JSON data
# data = json.load(open('context_changes_human/filtered_total_change.json', 'r'))
# count = 0
# for key in data.keys():
#     count += len(data[key])
# print(count)


# Function to load scene annotations
def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)
    
annotations = load_scene_annotations()

def format_faces_for_pyvista(faces):
    # Each face needs to start with the number of vertices (3 for triangles)
    num_faces = faces.shape[0]
    # Create an array where each triangle face is prefixed by the number 3 (for triangles)
    faces_formatted = np.hstack([[3, face[0], face[1], face[2]] for face in faces])
    return faces_formatted


add = json.load(open('context_changes_human/filtered_add_responses.json', 'r'))
replace = json.load(open('context_changes_human/filtered_removal_responses.json', 'r'))
delete = json.load(open('context_changes_human/filtered_replace_responses.json', 'r'))
move = json.load(open('context_changes_human/filtered_move_responses.json', 'r'))

GPT_add = json.load(open('GPT_context_changes/filtered_add_remove_changes.json', 'r'))
GPT_attri = json.load(open('GPT_context_changes/filtered_attribute_changes.json', 'r'))
GPT_move = json.load(open('GPT_context_changes/filtered_move_changes.json', 'r'))

data = {}
for key in GPT_move.keys():
    data[key] = []

for key in add.keys():
    scene_id = "_".join(key.split('_')[2:-1]).strip()
    for change in add[key]:
        data[scene_id].append(change)

for key in replace.keys():
    scene_id = "_".join(key.split('_')[2:-1]).strip()
    for change in replace[key]:
        data[scene_id].append(change)
        
for key in delete.keys():
    scene_id = "_".join(key.split('_')[2:]).strip()
    for change in delete[key]:
        data[scene_id].append(change)
        
for key in move.keys():
    scene_id = "_".join(key.split('_')[2:-1]).strip()
    for change in move[key]:
        data[scene_id].append(change)
        
# for key in GPT_add.keys():
#     scene_id = "_".join(key.split('_')[:-1]).strip()
#     for change in GPT_add[key]:
#         data[scene_id].append(change)

# for key in GPT_attri.keys():
#     scene_id = "_".join(key.split('_')[:-1]).strip()
#     for change in GPT_attri[key]:
#         data[scene_id].append(change)
        
# for key in GPT_move.keys():
#     scene_id = "_".join(key.split('_')[:]).strip()
#     for change in GPT_move[key]:
#         data[scene_id].append(change)
        
for key in data.keys():
    data[key] = list(set(data[key]))
    
length = sum([len(data[key]) for key in data.keys()])
print(f'Total changes: {length}')

# filter_data = {}
# failed = []
# failed_ids = []

# # # Loop through the data
# for key in data.keys():
# #     # Extract scene_id and human_id from the key
#     scene_id = key
#     # Skip if scene_id is 'None'
#     if scene_id == 'None':
#         continue
    
#     # Get annotations for the current scene
#     annotation = annotations.get(scene_id, [])
#     filter_data[key] = []
    
# #     # Loop through changes in the data associated with the key
    
#     for change in data[key]:
#         # Check if the change has fewer than 10 words, skip if true
#         if len(change.split()) < 8:
#             print(f'Scene ID: {scene_id} too short')
#             failed.append(change)
#             continue
        
#         if 'one of' in change or 'such as' in change:
#             print(f'Scene ID: {scene_id} one of')
#             failed.append(change)
#             continue
        
#         violate = True
#         # Loop through the annotations
#         for ann in annotation:
#             # Rereplace HTML tags and convert to lowercase for comparison
#             label = re.sub(r'<.*?>', '', ann['text']).lower()
#             # Check if the cleaned label exists in the change (case insensitive)
#             if label in change.lower():
#                 violate = False
        
#         # If more than 2 violations, mark the change as failed
#         if violate == True:
#             print(f'Scene ID: {scene_id}')
#             failed.append(change)
#             continue
        
#         # If no violation, append the change to filter_data
#         filter_data[key].append(change)
    
# with open('context_changes_human/filtered_total_change.json', 'w') as f:
#     json.dump(filter_data, f, indent=4)

#     Load the .npz file with the 3D scan data
    # ply_file = f'3D_scans/{scene_id}/{scene_id}_filtered_vh_clean_2.npz'
    # npz_data = np.load(ply_file)

    # # Assuming the .npz file contains 'vertices', 'faces', and 'vertex_colors'
    # vertices = npz_data['vertices']  # Replace with actual key names from the .npz file
    # faces = npz_data['faces']  # Replace with actual key names from the .npz file
    # colors = npz_data['vertex_colors']  # Replace with actual key names from the .npz file
    
    # faces = format_faces_for_pyvista(faces)


    # Create a mesh in PyVista from vertices and faces
    # mesh = pv.PolyData(vertices, faces)

    # # removal vertex colors to the mesh (if available)
    # if colors is not None:
    #     mesh.point_data['colors'] = colors

    # # Create a PyVista plotter for visualizing the mesh
    # plotter = pv.Plotter()

    # # removal the mesh to the plotter
    # plotter.removal_mesh(mesh, scalars='colors', rgb=True)

    # # removal annotations as spheres and text labels
    # if scene_id in annotations:
    #     for annotation in annotations[scene_id]:
    #         label = re.sub(r'<.*?>', '', annotation['text'])
    #         position = annotation['x'], annotation['y'], annotation['z']

    #         # Create a sphere for each annotation
    #         sphere = pv.Sphere(radius=0.02, center=position)
    #         plotter.removal_mesh(sphere, color='red')

    #         # removal a text label at the annotation position
    #         plotter.removal_point_labels([position], [label], point_size=10, text_color="blue", font_size=15,always_visible=True)

    # # Display the visualization
    # plotter.show()

        
    # Filter out wall and ceiling vertices
    
    



# import plotly.graph_objects as go
# import numpy as np
# import os
# import msgpack
# import plotly.io as pio
# import json
# import open3d as o3d

# ROOT_1 = "3D_scans"
# SCENE_IDs = sorted([scene for scene in os.listdir(ROOT_1) if not scene.startswith('scene')])[:200]
# SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

# # scene_ids = [scene.split('.png')[0] for scene in os.listdir('top_views_annotated') if not scene.startswith('scene')]

# # # sort ids with 1.png, 2.png, 3.png, ...
# # scene_ids = sorted(scene_ids, key=lambda x: int(x.split('.png')[0]))

# # # rename scene ids with SCENE_IDs
# # for i, scene_id in enumerate(SCENE_IDs):

# #     print(f'top_views_annotated/{scene_ids[i]}.png', f'top_views_annotated/{scene_id}.png')
# #     # os.rename(f'top_views_annotated/{scene_ids[i]}.png', f'top_views_annotated/{scene_id}.png')
# # breakpoint()

# def load_mesh(ply_file):
#     return np.load(ply_file, allow_pickle=True, mmap_mode='r')

# def plot_mesh(vertices, triangles, vertex_colors, annotations):
#     vertex_colors_rgb = [f'rgb({r}, {g}, {b})' for r, g, b in vertex_colors]

#     mesh = go.Mesh3d(
#         x=vertices[:, 0],
#         y=vertices[:, 1],
#         z=vertices[:, 2],
#         i=triangles[:, 0],
#         j=triangles[:, 1],
#         k=triangles[:, 2],
#         vertexcolor=vertex_colors_rgb,
#         opacity=1.0
#     )

#     fig = go.Figure(data=[mesh])

#     fig.update_layout(
#         scene=dict(
#             aspectmode='data',
#             xaxis=dict(visible=False),
#             yaxis=dict(visible=False),
#             zaxis=dict(visible=False),
#             annotations=annotations,
#         ),
#     )
    
#     pio.show(fig)

# def load_scene_annotations():
#     with open('scene_annotations.msgpack', 'rb') as file:
#         return msgpack.unpack(file, raw=False)

# scene_annotations = load_scene_annotations()

# def load_json(file_path):
#     with open(file_path, 'r') as file:
#         return json.load(file)
    
# def read_instance_labels(scene_id):
#     return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

# def filter_vertices_labels(vertices, triangles, vertex_colors, labels, exclude_labels):
#     mask = np.isin(labels, exclude_labels, invert=True)
#     filtered_vertices = vertices[mask]
#     filtered_vertex_colors = vertex_colors[mask]

#     # Filtering triangles that have all vertices in the mask
#     # valid_triangles = np.all(mask[triangles], axis=1)
#     index_map = np.full(mask.shape[0], -1)
#     index_map[mask] = np.arange(np.sum(mask))

#     # Filter triangles that have all vertices in the mask
#     valid_triangles = np.all(mask[triangles], axis=1)
#     filtered_triangles = triangles[valid_triangles]
    
#     # Remap the indices of the triangles to the new vertex indices
#     filtered_triangles = index_map[filtered_triangles]
#     return filtered_vertices, filtered_triangles, filtered_vertex_colors

# # Define your wall and ceiling labels here (you need to know the labels for your dataset)

# # for scene_id in SCENE_IDs[180:200]:
# scene_id ='6bde60cb-9162-246f-8cf5-d04f7426e56f'
# id2labels = read_instance_labels(scene_id)

# print(scene_id)
# WALL_CEILING_LABELS = [int(k) for k, v in id2labels.items() if 'wall' in v or 'ceiling' in v]

# # Load the mesh data from the .ply file
# ply_file = SCENE_ID_TO_FILE[scene_id]
# mesh_data = load_mesh(ply_file)
# vertices, triangles, vertex_colors = mesh_data.values()

# # Load the vertex labels from the NPZ file
# label_path = f'3D_scans/{scene_id}/{scene_id}_instance_labels.npy'
# labels = np.load(label_path)

# # Filter out wall and ceiling vertices
# filtered_vertices, filtered_triangles, filtered_vertex_colors = filter_vertices_labels(vertices, triangles, vertex_colors[:,:3], labels, WALL_CEILING_LABELS)

# # Plot the filtered mesh
# plot_mesh(filtered_vertices, filtered_triangles, filtered_vertex_colors, scene_annotations[scene_id])

