import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import json
import open3d as o3d
import numpy as np
import trimesh
import os

ROOT_2 = "/mnt/sda/"

# read json

count = 0
with open(os.path.join(ROOT_2, "3RScan.json")) as f:
    data = json.load(f)
    scene_ids = [scene["reference"] for scene in data]
    
    for scene in data:
        scene_id = scene["reference"]
        scene_path = os.path.join(ROOT_2, '3rscan', scene_id, 'mesh.refined.v2.npz')
        label_path = os.path.join(ROOT_2, '3rscan', scene_id, 'labels.instances.annotated.v2.npy')
        
        scene_data = np.load(scene_path)
        label_data = np.load(label_path)
            
        if scene_data['vertices'].shape[0] != label_data.shape[0]:
            count += 1
            # for i in np.unique(label_data):
            #     print("Label:", i, "Count:", np.sum(label_data == i))
            # breakpoint()
            
print(count)
        

