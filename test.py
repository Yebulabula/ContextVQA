import numpy as np
import json
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
ROOT_1 = "3D_scans"

def read_instance_labels(scene_id):
    instance_labels = np.load(f'{ROOT_1}/{scene_id}/{scene_id}_instance_labels.npy')
    with open(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json', 'r') as json_file:
        id2labels = json.load(json_file)
    return instance_labels, id2labels

def read_scene_mesh(scene_id):
    mesh_path = f'{ROOT_1}/{scene_id}/{scene_id}_vh_clean_2.npz'
    scene_data = np.load(mesh_path, allow_pickle=True)
    vertices, faces, vertexcolor = scene_data.values()
    
     
    # mesh_path = f'{ROOT_1}/{scene_id}/{scene_id}_vh_clean_0.obj'
    # mesh = o3d.io.read_triangle_mesh(mesh_path)
    # if not mesh.has_vertex_normals():
    #     mesh.compute_vertex_normals()
        
    return vertices, faces, vertexcolor

def plot_scene_with_labels(scene_id, vertices, faces, vertex_colors, instance_labels, id2labels):
    # Exclude the ceiling category
    print(id2labels)
    ceiling_indices = [int(id) for id, label in id2labels.items() if 'ceiling' in label]
    mask = np.isin(instance_labels, ceiling_indices, invert=True)

    filtered_vertices = vertices[mask]
    filtered_vertex_colors = vertex_colors[mask]
    filtered_instance_labels = instance_labels[mask]
    
    
    # Create a mapping from old vertex indices to new vertex indices
    old_to_new_index = {old_idx: new_idx for new_idx, old_idx in enumerate(np.where(mask)[0])}
    
    # Filter faces to only include those with vertices in the new set
    filtered_faces = []
    for face in faces:
        if all(vertex in old_to_new_index for vertex in face):
            new_face = [old_to_new_index[vertex] for vertex in face]
            filtered_faces.append(new_face)
    
    filtered_faces = np.array(filtered_faces)
    
    # Create subplots with 1 row and 2 columns, with reduced horizontal spacing
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'mesh3d'},]])

    # # Plot original mesh
    x, y, z = filtered_vertices.T
    i, j, k = filtered_faces.T
    
    # x, y, z = vertices.T
    # i, j, k = faces.T
    
    # # Apply color coding based on depth (z-axis)
    # colorscale = 'Greys'
    # color_intensity = np.interp(z, (z.min(), z.max()), (0, 255))
    
    trace_mesh_gray = go.Mesh3d(
        x=x, y=y, z=z, 
        i=i, j=j, k=k, 
        vertexcolor=filtered_vertex_colors, 
        opacity=1.0, 
        name='Original Mesh'
    )
    
    # save_path = f'/mnt/new_drive/Documents/ContextVQA/3D_scans/{scene_id}/{scene_id}_filtered_vh_clean_2.npz'
    # np.savez(save_path, 
    #          vertices=filtered_vertices, 
    #          faces=filtered_faces,
    #          vertex_colors=filtered_vertex_colors)
    
    # breakpoint()


    # Plot light gray mesh
    # trace_mesh_gray = go.Mesh3d(
    #     x=x, y=y, z=z, 
    #     i=i, j=j, k=k, 
    #     opacity=0.9, 
    #     intensity=color_intensity,
    #     colorscale='plasma',
    #     name='Gray Mesh'
    # )

    # Prepare labels
    caption = 'The scene contains the following objects: '
    objects_by_category = {}
    for instance_id, label in id2labels.items():
        category = label.split('_')[0]
        # if category == 'wall' or category == 'object' or category == 'floor' or category == 'ceiling':
        #     continue
        if category not in objects_by_category:
            objects_by_category[category] = []
        objects_by_category[category].append(label)
    
    for category in objects_by_category:
        if len(objects_by_category[category]) > 1:
            caption += f'{len(objects_by_category[category])} {category}s, '
        else:
            caption += f'{len(objects_by_category[category])} {category}, '    
    
    # Find good positions for category labels (using centroids of the instances)
    annotations = []
    markers = []
    for instance_id, label in id2labels.items():
        category = label
        # print(label)
        # if category == 'wall' or category == 'object' or category == 'floor' or category == 'ceiling':
        #     continue
        instance_indices = np.where(filtered_instance_labels == int(instance_id))[0]
        
        if len(instance_indices) > 0:
            instance_points = filtered_vertices[instance_indices]
            centroid = np.mean(instance_points, axis=0)
            opacity = centroid[2] / z.max() + 0.03  # Scale opacity based on height
            annotations.append(dict(
                x=centroid[0],
                y=centroid[1],
                z=centroid[2],
                text=f'{category}',
                showarrow=False,
                font=dict(size=12, color='cyan'),
                xanchor='center',
                # xshift=10,
            ))  
            
            markers.append(go.Scatter3d(
                x=[centroid[0]], y=[centroid[1]], z=[centroid[2]],
                mode='markers',
                marker=dict(size=5, color='red'),
                showlegend=False
            ))

    fig.add_trace(trace_mesh_gray)
    
        
    fig.update_layout(scene=dict(annotations=annotations))
    # Update layout
    fig.update_layout(scene=dict(aspectmode='data'))
    # Hide axis in both subplots
    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False))
    )
    
    # Reduce the margins and padding
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
    fig.show()
    
    return caption

scenes = sorted([scene_id for scene_id in os.listdir(ROOT_1) if not scene_id.startswith('scene')])
for scene_id in scenes:
    # if scene_id == 'scene0038_00':
    print(scene_id)
    instance_labels, id2labels = read_instance_labels(scene_id)
    vertices, faces, vertex_colors = read_scene_mesh(scene_id)
    plot_scene_with_labels(scene_id, vertices, faces, vertex_colors, instance_labels, id2labels)
    
    # print(caption)
    breakpoint()

# import numpy as np 
# import os


# for idx, scene_id in os.listdir('/mnt/new_drive/Documents/ContextVQA/3D_scans'):
    i, j, k = faces.T