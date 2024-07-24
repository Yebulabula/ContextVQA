import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

# # Load the point cloud file
# ply_file = '/mnt/sda/scannet/raw/scans/scene0000_00/scene0000_00_vh_clean_2.ply'
# point_cloud = o3d.io.read_point_cloud(ply_file)

# # Load the segmentation labels file using Open3D
# seg_file = '/mnt/sda/scannet/raw/scans/scene0000_00/scene0000_00_vh_clean_2.labels.ply'
# seg_mesh = o3d.io.read_point_cloud(seg_file)

# # Extract segmentation labels from the color attribute
# seg_labels = np.asarray(seg_mesh.colors)[:, 0]  # Assuming the label is stored in the red channel

# # Map segmentation labels to colors
# unique_labels = np.unique(seg_labels)
# colors = plt.get_cmap("tab20")(np.linspace(0, 1, len(unique_labels)))[:, :3]  # Generate a color map

# # Create a mapping from label to color
# label_to_color = {label: colors[i] for i, label in enumerate(unique_labels)}

# # Assign colors to the point cloud based on segmentation labels
# point_colors = np.array([label_to_color[label] for label in seg_labels])

# point_cloud.colors = o3d.utility.Vector3dVector(point_colors)

# # Visualize the point cloud with segmentation labels
# o3d.visualization.draw_geometries([point_cloud])

import open3d as o3d
import numpy as np
import json
from plyfile import PlyData

data = np.load('/mnt/sda/3rscan/6a360523-fa53-2915-9506-4b95fa02cc56/labels.instances.annotated.v2.npy')

# load .ply file
ply_file = '/mnt/sda/3rscan/6a360523-fa53-2915-9506-4b95fa02cc56/labels.instances.annotated.v2.ply'
point_cloud = o3d.io.read_point_cloud(ply_file)
breakpoint()
def process_instance_labels(sem_file, segs_file, agg_file):
    try:
        with open(sem_file, "rb") as f:
            plydata = PlyData.read(f)
    except:
        return None, None
        
    if 'label' in plydata.elements[0].data.dtype.names:
        sem_labels = np.array(plydata.elements[0]["label"]).astype(np.int64)
    else:
        sem_labels = np.array(plydata.elements[0]["objectId"]).astype(np.int64)
        
    with open(segs_file, "r") as f:
        d = json.load(f)
        seg = d["segIndices"]
        segid_to_pointid = {}
        for i, segid in enumerate(seg):
            segid_to_pointid.setdefault(segid, []).append(i)

    instance_class_labels = []
    instance_segids = []
    with open(agg_file, "r") as f:
        d = json.load(f)
    for i, x in enumerate(d["segGroups"]):
        instance_class_labels.append(f"{x['label']}_{x['objectId']}")
        instance_segids.append(x["segments"])

    instance_labels = np.ones(sem_labels.shape[0], dtype=np.int64) * -100
    for i, segids in enumerate(instance_segids):
        pointids = []
        for segid in segids:
            pointids += segid_to_pointid[segid]
        instance_labels[pointids] = i

    id2labels = {i: label for i, label in enumerate(instance_class_labels)}
    return instance_labels, id2labels

# instance_labels, id2labels = process_instance_labels('/mnt/sda/3rscan/6a360523-fa53-2915-9506-4b95fa02cc56/labels.instances.annotated.v2.ply', '/mnt/sda/3rscan/6a360523-fa53-2915-9506-4b95fa02cc56/labels.instances.annotated.v2.segs.json', '/mnt/sda/3rscan/6a360523-fa53-2915-9506-4b95fa02cc56/labels.instances.annotated.v2.aggregation.json')