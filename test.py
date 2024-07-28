# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output
# import plotly.graph_objects as go
# import json
# import open3d as o3d
# import numpy as np
# import trimesh
# import os

# ROOT_2 = "/mnt/sda/"

# # read json

# count = 0
# with open(os.path.join(ROOT_2, "3RScan.json")) as f:
#     data = json.load(f)
#     scene_ids = [scene["reference"] for scene in data]
    
#     for scene in data:
#         scene_id = scene["reference"]
#         scene_path = os.path.join(ROOT_2, '3rscan', scene_id, 'mesh.refined.v2.npz')
#         label_path = os.path.join(ROOT_2, '3rscan', scene_id, 'labels.instances.annotated.v2.npy')
        
#         scene_data = np.load(scene_path)
#         label_data = np.load(label_path)
            
#         if scene_data['vertices'].shape[0] != label_data.shape[0]:
#             count += 1
#             # for i in np.unique(label_data):
#             #     print("Label:", i, "Count:", np.sum(label_data == i))
#             # breakpoint()
            
# print(count)


import numpy as np
import json

ROOT_1 = "3D_scans"
def read_instance_labels(scene_id):
    instance_labels = np.load(f'{ROOT_1}/{scene_id}/{scene_id}_instance_labels.npy')
    print(f'{ROOT_1}/{scene_id}/{scene_id}_instance_labels.npy')
    with open(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json', 'r') as json_file:
        id2labels = json.load(json_file)
    return instance_labels, id2labels

scene_id = 'scene0000_00'
instance_labels, id2labels = read_instance_labels(scene_id)

caption = 'The scene contains the following objects: '
objects_by_category = {}
for instance_id, label in id2labels.items():
    category = label.split('_')[0]
    if category == 'wall' or category == 'object'or category == 'floor':
        continue
    if category not in objects_by_category:
        objects_by_category[category] = []
    objects_by_category[category].append(label)
    

for category in objects_by_category:
    if len(objects_by_category[category]) > 1:
        caption += f'{len(objects_by_category[category])} {category}s, '
    else:
        caption += f'{len(objects_by_category[category])} {category}, '    
        
print(caption)
breakpoint()