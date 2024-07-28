import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import os

def load_mesh_from_npz(npz_path):
    # Load data from npz file
    mesh_data = np.load(npz_path, allow_pickle=True, mmap_mode='r')
    vertices, triangles, vertex_colors = mesh_data.values()
    print(vertex_colors.shape)
    rgb_colors = vertex_colors[:, :3]
    if rgb_colors.max() > 1.0:
        rgb_colors = rgb_colors / 255.0

    # Create an Open3D TriangleMesh object
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    mesh.vertex_colors = o3d.utility.Vector3dVector(rgb_colors.astype(np.float64))
    return mesh

def load_mesh_from_ply(ply_path):
    # Load the mesh from the file
    mesh = o3d.io.read_triangle_mesh(ply_path)
    if not mesh.has_vertex_normals():
        mesh.compute_vertex_normals()
    return mesh

def visualize_meshes(mesh1, mesh2):
    # Translate mesh2 to the right of mesh1
    bounding_box1 = mesh1.get_axis_aligned_bounding_box()
    bounding_box2 = mesh2.get_axis_aligned_bounding_box()

    # Calculate offset to position mesh2 beside mesh1
    offset = bounding_box1.get_extent() + bounding_box2.get_extent()
    mesh2.translate([offset[0], 0, 0], relative=False)  # Translate mesh2 on the x-axis

    # Visualize both meshes together
    # o3d.visualization.draw_geometries([mesh1])
    o3d.visualization.draw_geometries([mesh2])

files = sorted(os.listdir('3D_scans'))
for scene_id in files:
    if scene_id.startswith('scene'):
        ply_path = f'/mnt/new_drive/Documents/scans/{scene_id}/{scene_id}_vh_clean.ply'
        npz_path = f'/mnt/new_drive/Documents/scans/{scene_id}/{scene_id}_vh_clean_2.labels.ply'  # Assuming NPZ path follows this pattern
        if os.path.exists(ply_path) and os.path.exists(npz_path):
            mesh1 = load_mesh_from_ply(ply_path)
            mesh2 = load_mesh_from_ply(npz_path)
            visualize_meshes(mesh1, mesh2)
