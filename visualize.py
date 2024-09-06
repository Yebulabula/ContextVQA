import plotly.graph_objects as go
import numpy as np
import os
import msgpack
import plotly.io as pio
import json
import open3d as o3d

ROOT_1 = "3D_scans"
SCENE_IDs = sorted([scene for scene in os.listdir(ROOT_1) if not scene.startswith('scene')])[:200]
SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

# scene_ids = [scene.split('.png')[0] for scene in os.listdir('top_views_annotated') if not scene.startswith('scene')]

# # sort ids with 1.png, 2.png, 3.png, ...
# scene_ids = sorted(scene_ids, key=lambda x: int(x.split('.png')[0]))

# # rename scene ids with SCENE_IDs
# for i, scene_id in enumerate(SCENE_IDs):

#     print(f'top_views_annotated/{scene_ids[i]}.png', f'top_views_annotated/{scene_id}.png')
#     # os.rename(f'top_views_annotated/{scene_ids[i]}.png', f'top_views_annotated/{scene_id}.png')
# breakpoint()

def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

def plot_mesh(vertices, triangles, vertex_colors, annotations):
    vertex_colors_rgb = [f'rgb({r}, {g}, {b})' for r, g, b in vertex_colors]

    mesh = go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=triangles[:, 0],
        j=triangles[:, 1],
        k=triangles[:, 2],
        vertexcolor=vertex_colors_rgb,
        opacity=1.0
    )

    fig = go.Figure(data=[mesh])

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            annotations=annotations,
        ),
    )
    
    pio.show(fig)

def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)

scene_annotations = load_scene_annotations()

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def read_instance_labels(scene_id):
    return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

def filter_vertices_labels(vertices, triangles, vertex_colors, labels, exclude_labels):
    mask = np.isin(labels, exclude_labels, invert=True)
    filtered_vertices = vertices[mask]
    filtered_vertex_colors = vertex_colors[mask]

    # Filtering triangles that have all vertices in the mask
    # valid_triangles = np.all(mask[triangles], axis=1)
    index_map = np.full(mask.shape[0], -1)
    index_map[mask] = np.arange(np.sum(mask))

    # Filter triangles that have all vertices in the mask
    valid_triangles = np.all(mask[triangles], axis=1)
    filtered_triangles = triangles[valid_triangles]
    
    # Remap the indices of the triangles to the new vertex indices
    filtered_triangles = index_map[filtered_triangles]
    return filtered_vertices, filtered_triangles, filtered_vertex_colors

# Define your wall and ceiling labels here (you need to know the labels for your dataset)

# for scene_id in SCENE_IDs[180:200]:
scene_id ='6bde60cb-9162-246f-8cf5-d04f7426e56f'
id2labels = read_instance_labels(scene_id)

print(scene_id)
WALL_CEILING_LABELS = [int(k) for k, v in id2labels.items() if 'wall' in v or 'ceiling' in v]

# Load the mesh data from the .ply file
ply_file = SCENE_ID_TO_FILE[scene_id]
mesh_data = load_mesh(ply_file)
vertices, triangles, vertex_colors = mesh_data.values()

# Load the vertex labels from the NPZ file
label_path = f'3D_scans/{scene_id}/{scene_id}_instance_labels.npy'
labels = np.load(label_path)

# Filter out wall and ceiling vertices
filtered_vertices, filtered_triangles, filtered_vertex_colors = filter_vertices_labels(vertices, triangles, vertex_colors[:,:3], labels, WALL_CEILING_LABELS)

# Plot the filtered mesh
plot_mesh(filtered_vertices, filtered_triangles, filtered_vertex_colors, scene_annotations[scene_id])

