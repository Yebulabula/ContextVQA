import open3d as o3d
import numpy as np


def visualize_mesh(mesh_file):
    data =np.load(mesh_file)
    
    # Split the data into coordinates, colors, and normals
    coordinates = data[:, 0:3]
    colors = data[:, 3:6] / 255.0  # Normalizing the RGB values to [0, 1]
    normals = data[:, 6:9]

    # Create an Open3D point cloud
    point_cloud = o3d.geometry.PointCloud()

    # Assign the data to the point cloud
    point_cloud.points = o3d.utility.Vector3dVector(coordinates)
    point_cloud.colors = o3d.utility.Vector3dVector(colors)
    point_cloud.normals = o3d.utility.Vector3dVector(normals)
    
    return point_cloud
    
# File paths
mesh_file = '/mnt/new_drive/Documents/ContextQA/ScanQA/data/scannet/scannet_data/scene0000_00_aligned_vert.npy'
bbox_file = '/mnt/new_drive/Documents/ContextQA/ScanQA/data/scannet/scannet_data/scene0000_00_bbox.npy'

# Load the mesh
# mesh = o3d.io.read_triangle_mesh(mesh_file)
# mesh.compute_vertex_normals()

mesh = visualize_mesh(mesh_file)

# Load the bounding boxes
bboxes = np.load(bbox_file)

# Print bounding box data to understand its structure
print("Bounding box data shape:", bboxes.shape)
print("Bounding box data example:", bboxes[0])

# Convert bounding boxes to Open3D format
bbox_linesets = []
for bbox in bboxes:
    print(bbox)
    breakpoint()
    
    # Extract bounding box parameters
    center = bbox[:3]
    extent = bbox[3:6]
    
    # Create the OrientedBoundingBox
    obb = o3d.geometry.OrientedBoundingBox()
    obb.center = center
    obb.extent = extent
    
    # Apply rotation around the Z-axis (assuming bbox[6] is the rotation angle around Z)
    # R = o3d.geometry.OrientedBoundingBox.get_rotation_matrix_from_xyz((0, 0, rotation_angle))
    # obb = obb.rotate(R, center)  
    
    # Create lineset from bounding box
    lineset = o3d.geometry.LineSet.create_from_oriented_bounding_box(obb)
    lineset.paint_uniform_color([1, 0, 0])  # Red color for bounding boxes
    bbox_linesets.append(lineset)

# Visualize the mesh and bounding boxes
o3d.visualization.draw_geometries([mesh, *bbox_linesets])