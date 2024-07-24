import open3d as o3d
import numpy as np
import os

# def load_mesh(ply_file):
#     mesh = o3d.io.read_triangle_mesh(ply_file)
#     vertices = np.asarray(mesh.vertices)
#     triangles = np.asarray(mesh.triangles)
#     vertex_colors = np.asarray(mesh.vertex_colors)
#     return vertices, triangles, vertex_colors

# ROOT = "scannet"
# SCENE_IDs = os.listdir(ROOT)
# SCENE_IDs.sort()
# SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT, scene_id, f'{scene_id}_vh_clean_2.ply') for scene_id in SCENE_IDs}

# for scene_id, ply_file in SCENE_ID_TO_FILE.items():
#     vertices, triangles, vertex_colors = load_mesh(ply_file)
#     print(scene_id, vertices.shape, triangles.shape, vertex_colors.shape)
#     save_file = os.path.join(ROOT, scene_id, f'{scene_id}_vh_clean_2.npz')
#     np.savez(save_file, vertices=vertices, triangles=triangles, vertex_colors=vertex_colors)

print(np.load('scannet/scene0000_00/scene0000_00_vh_clean_2.npz')['vertices'].shape)
    
    