import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import random


ROOT_1 = "3D_scans"

SCENE_IDs = sorted(os.listdir(ROOT_1), key=lambda x: (not x.startswith('scene'), x))

SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

def read_instance_labels(scene_id):
    instance_labels = np.load(f'{ROOT_1}/{scene_id}/{scene_id}_instance_labels.npy')
    with open(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json', 'r') as json_file:
        id2labels = json.load(json_file)
    return instance_labels, id2labels

scene_annotations = dict.fromkeys(SCENE_IDs)

for scene_id in SCENE_IDs:
    print(f'Processing {scene_id}...')
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    vertex_colors = vertex_colors[:, :3]

    instance_labels, id2labels = read_instance_labels(scene_id)
    id2labels = {int(k): v for k, v in id2labels.items()}

    excluded_categories = {'wall', 'object', 'floor', 'ceiling'}
    annotations = []
    
    for instance_id, label in id2labels.items():
        # Split label and check if category is excluded
        category = label.split('_', 1)[0]
        if category in excluded_categories:
            continue

        # Filter instance indices
        instance_id_int = int(instance_id)
        instance_indices = np.flatnonzero(instance_labels == instance_id_int)
        if instance_indices.size == 0:
            continue

        # Calculate centroid using vectorized operations
        centroid = np.mean(vertices[instance_indices], axis=0)

        # Append annotation
        annotations.append({
            'x': centroid[0],
            'y': centroid[1],
            'z': centroid[2],
            'text': f'<b>{category}</b>',
            'showarrow': False,
            'font': {'size': 12, 'color': 'yellow'},
            'xanchor': 'center'
        })
    scene_annotations[scene_id] = annotations
    # print(f'{scene_id} annotations: {len(annotations)}')
    
# save annotations to json file
with open('scene_annotations.json', 'w') as json_file:
    json.dump(scene_annotations, json_file)
   
# breakpoint()

# import numpy as np
# import json 

# file = '3D_scans/2e36953b-e133-204c-931b-a2cf0f93fed6/2e36953b-e133-204c-931b-a2cf0f93fed6.aggregation.json'
# with open(file, 'r') as f:
#     data = json.load(f)
#     for i in range(len(data['segGroups'])):
#         print(data['segGroups'][i]['label'])

# print(data.shape)