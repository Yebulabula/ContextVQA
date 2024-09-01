# import streamlit as st
# import plotly.graph_objects as go
# import os
# import numpy as np
# import json
# from plyfile import PlyData
# import time
# from plotly.subplots import make_subplots
# import random

# # Streamlit app
# st.set_page_config(
#     page_title="ContextQA Data Collection App",
#     page_icon="🧊",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'Get Help': 'https://www.extremelycoolapp.com/help',
#         'Report a bug': "https://www.extremelycoolapp.com/bug",
#         'About': "# This is a header. This is an *extremely* cool app!"
#     }
# )
# st.title("ContextQA")

# ROOT_1 = "3D_scans"

# # ROOT_VQA = '/mnt/new_drive/Documents/3D-VLM/Chat-3D-v2'
# # file_names = ['annotations/scanqa/ScanQA_v1.0_train.json', 'annotations/scanqa/ScanQA_v1.0_val.json', 'annotations/scanqa/ScanQA_v1.0_test_w_obj.json', 'annotations/scanqa/ScanQA_v1.0_test_wo_obj.json']
# # sqa3d_names = ['annotations/sqa3d/v1_balanced_questions_train_scannetv2.json', 'annotations/sqa3d/v1_balanced_questions_train_scannetv2.json', 'annotations/sqa3d/v1_balanced_questions_val_scannetv2.json', 'annotations/sqa3d/v1_balanced_questions_test_scannetv2.json']

# # seed = 42
# # @st.cache_data
# # def load_scene_ids(file_names, root_vqa, dataset = 'scanqa'):
# #     scene_ids = []
# #     for file_name in file_names:
# #         vqa_file = os.path.join(root_vqa, file_name)
# #         with open(vqa_file) as f:
# #             data = json.load(f) if dataset == 'scanqa' else json.load(f)['questions']

# #             scene_ids.extend([item['scene_id'] for item in data])
# #     return set(scene_ids)

# # scanqa_scene_ids = load_scene_ids(file_names, ROOT_VQA, 'scanqa')
# # sqa3d_scene_ids = load_scene_ids(sqa3d_names, ROOT_VQA,'sqa3d')

# # scanqa_scene_ids = set(scanqa_scene_ids)
# # sqa3d_scene_ids = set(sqa3d_scene_ids)

# # random_instance = random.Random(seed)

# # SCENE_IDs = list(sqa3d_scene_ids.intersection(scanqa_scene_ids))

# SCENE_IDs = os.listdir(ROOT_1)


# SCENE_IDs.sort()
# SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

# def process_instance_labels(sem_file, segs_file, agg_file):
#     print(sem_file)
#     with open(sem_file, "rb") as f:
#         plydata = PlyData.read(f)
        
#     if 'label' in plydata.elements[0].data.dtype.names:
#         sem_labels = np.array(plydata.elements[0]["label"]).astype(np.int64)
#     else:
#         sem_labels = np.array(plydata.elements[0]["objectId"]).astype(np.int64)
        
#     with open(segs_file, "r") as f:
#         d = json.load(f)
#         seg = d["segIndices"]
#         segid_to_pointid = {}
#         for i, segid in enumerate(seg):
#             segid_to_pointid.setdefault(segid, []).append(i)

#     instance_class_labels = []
#     instance_segids = []
#     with open(agg_file, "r") as f:
#         d = json.load(f)
#     for i, x in enumerate(d["segGroups"]):
#         instance_class_labels.append(f"{x['label']}_{x['objectId']}")
#         instance_segids.append(x["segments"])

#     instance_labels = np.ones(sem_labels.shape[0], dtype=np.int64) * -100
#     for i, segids in enumerate(instance_segids):
#         pointids = []
#         for segid in segids:
#             pointids += segid_to_pointid[segid]
#         instance_labels[pointids] = i

#     id2labels = {i: label for i, label in enumerate(instance_class_labels)}
#     return instance_labels, id2labels

# # for id in SCENE_IDs:
# #     for file in os.listdir(f'{ROOT_1}/{id}'):
# #         if file.endswith('2.0.010000.segs.json'):
# #         # remove the ply file
# #             os.system(f'rm {ROOT_1}/{id}/{file}')
    
#     # if id.startswith('scene'):
#     #     instance_labels, id2labels = process_instance_labels(SCENE_ID_TO_LABEL[id], SCENE_ID_TO_SEGS[id], SCENE_ID_TO_AGG[id])
#     #     np.save(f'{ROOT_1}/{id}/{id}_instance_labels.npy', instance_labels)
#     #     with open(f'{ROOT_1}/{id}/{id}_id2labels.json', 'w') as json_file:
#     #         json.dump(id2labels, json_file)
#         # cp id2lables to the folder
#         # os.system(f'cp /mnt/sda/3rscan/{id}/id2labels.json {ROOT_1}/{id}/{id}_id2labels.json')
        
# # breakpoint()

# @st.cache_data
# def read_instance_labels(scene_id, dataset = 'scannet'):
#     instance_labels = np.load(f'{ROOT_1}/{scene_id}/{scene_id}_instance_labels.npy')
#     with open(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json', 'r') as json_file:
#         id2labels = json.load(json_file)
#     return instance_labels, id2labels
    
# def load_mesh(ply_file):
#     if ply_file.endswith('.npz'):
#         return np.load(ply_file, allow_pickle=True, mmap_mode='r')

# def initialize_plot(vertices, triangles, vertex_colors, instance_labels, id2labels):
#     x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
#     i, j, k = triangles[:, 0], triangles[:, 1], triangles[:, 2]

#     vertex_colors_rgb = ['rgb({}, {}, {})'.format(r, g, b) for r, g, b in vertex_colors]
    
#     # trace2 for the instance labels
#     colors = np.zeros((instance_labels.shape[0], 3), dtype=np.uint8)
#     hovertext = [''] * instance_labels.shape[0]
    
#     for instance_id in np.unique(instance_labels):
#         if instance_id == -100:
#             continue
#         mask = instance_labels == instance_id
#         colors[mask] = np.random.randint(0, 255, size=(1, 3))
        
#         for index in np.where(mask)[0]:
#             hovertext[index] = id2labels[instance_id]
    
#     trace1 = go.Mesh3d(
#         x=x, y=y, z=z,
#         i=i, j=j, k=k,
#         vertexcolor=vertex_colors_rgb,
#         hovertext=hovertext,
#         opacity=1.0
#     )
    
#     fig = go.Figure(data=[trace1])
#     fig.update_layout(scene=dict(aspectmode='data'),
#                         width=2000,
#                         height=1500)

#     return fig, trace1

# def update_plot(fig, colors):
#     fig.update_traces(patch=dict(vertexcolor=['rgb({}, {}, {})'.format(r, g, b) for r, g, b in colors]))

# def get_semantic_category_counts(instance_labels, id2labels):
#     category_counts = {}
#     for instance_id in np.unique(instance_labels):
#         if instance_id == -100:
#             continue
#         label = id2labels.get(instance_id, 'Unknown')
#         category = label.split('_')[0]
#         if category in category_counts:
#             category_counts[category] += 1
#         else:
#             category_counts[category] = 1
#     return category_counts

# # Selectbox for scene selection
# old_scene_id = None
# scene_id = st.selectbox("Select a Scene ID", list(SCENE_ID_TO_FILE.keys()))
    
# if not os.path.exists('context_data.json'):
#     with open('context_data.json', 'w') as json_file:
#         json.dump([], json_file)

# if 'selected_label' not in st.session_state:
#         st.session_state.selected_label = None
        
# if scene_id:
#     # Get the corresponding .ply file for the selected scene ID
#     ply_file = SCENE_ID_TO_FILE[scene_id]

#     vertices, triangles, vertex_colors = load_mesh(ply_file).values()
#     vertex_colors = vertex_colors[:, :3]  # Remove the alpha channel
    
#     st.session_state.selected_label = None
#     instance_labels, id2labels = read_instance_labels(scene_id, 'scannet') if scene_id.startswith('scene') else read_instance_labels(scene_id, '3rscan')

#     labels2id = {v: int(k) for k, v in id2labels.items()}
#     id2labels = {int(k): v for k, v in id2labels.items()}

#     colors = vertex_colors
#     if scene_id != old_scene_id or 'trace' not in st.session_state:
#         old_scene_id = scene_id
#         mask = np.zeros(instance_labels.shape, dtype=bool)
#         st.session_state.fig, st.session_state.trace = initialize_plot(vertices, triangles, vertex_colors, instance_labels, id2labels)
#         # add_camera_sync(st.session_state.fig)
#         # Group objects by category and create expandable sections
#         st.sidebar.header("List of objects")
#         objects_by_category = {}
#         for instance_id, label in id2labels.items():
#             category = label.split('_')[0]
#             if category not in objects_by_category:
#                 objects_by_category[category] = []
#             objects_by_category[category].append(label)

#         for category, labels in objects_by_category.items():
#             expander_label = f"{category.capitalize()} | Amount: {len(labels)}"
#             with st.sidebar.expander(expander_label):
#                 for label in labels:
#                     if st.button(label, key=label):
#                         if st.session_state.selected_label == label:
#                             st.session_state.selected_label = None
#                         else:
#                             st.session_state.selected_label = label

#     st.markdown(
#         """
#         <style>
#         .label-entry {
#             background-color: #007bff;
#             color: white;
#             padding: 10px;
#             border-radius: 5px;
#             margin-bottom: 5px;
#             cursor: pointer;
#             transition: background-color 0.3s ease;
#         }
#         .label-entry.selected {
#             background-color: red;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )
    
#     # Initialize the visualization
#     st.markdown('<h2 class="scene-title">3D Scene Visualization</h2>', unsafe_allow_html=True)
    
#     if st.session_state.selected_label:
#         mask = (instance_labels == labels2id[st.session_state.selected_label])
    
#     # start_time = time.time()
#     # colors = vertex_colors.copy()  # Reset colors to original
#     # colors[mask] = [255, 0, 0]

#     # update_plot(st.session_state.fig, colors)
#     st.plotly_chart(st.session_state.fig, use_container_width=True)
#     # print("--- %s seconds ---" % (time.time() - start_time))

#     # Text boxes for Context Change, Question, and Answer
#     smaller_bold_context = """
#     <div style='font-weight: bold; font-size: 20px;'>
#         Step 1: Context Change
#     </div>
#     """
    
#     smaller_bold_question = """
#     <div style='font-weight: bold; font-size: 20px;'>
#         Step 2: Question
#     </div>
#     """
    
#     smaller_bold_answer = """
#     <div style='font-weight: bold; font-size: 20px;'>
#         Step 3: Answer
#     </div>
#     """
    
#     if 'data' not in st.session_state:
#         st.session_state.data = []

#     if 'responses_submitted' not in st.session_state:
#         st.session_state.responses_submitted = 0

#     if 'question_id' not in st.session_state:
#         with open('context_data.json', 'r') as json_file:
#             data = json.load(json_file)
#             st.session_state.question_id = int(data[-1]['question_id']) + 1
            
#     # Display the smaller bold text
#     st.markdown(smaller_bold_context, unsafe_allow_html=True, help="Write a short sentence describing the change of the 3D scene.")
#     context_change = st.text_area("Write a short sentence describing the change of the 3D scene.", key="context_change", help="Enter context change details here.", placeholder="Type here...", height=10)
    
#     # Define the available tags for the first set
#     tags_1 = [
#         "Object Geometric Change",
#         "Object Attribute Change",
#         "Object Addition or Removal"
#     ]

#     # Define the available tags for the second set
#     tags_2 = [
#         "Local Change",
#         "Global Change"
#     ]

#     # Allow the user to select tags from the first set
#     selected_tags_1 = st.selectbox("Select Type of Change", options=tags_1, key="selected_tags_1")

#     # Allow the user to select tags from the second set
#     selected_tags_2 = st.selectbox("Select Scale of Change", options=tags_2, key="selected_tags_2")

#     st.markdown(smaller_bold_question, unsafe_allow_html=True)
#     question = st.text_area("It is expected to be a sentence.", key="question", help="Enter your question here.", placeholder="Type here...", height=10)
    
#     st.markdown(smaller_bold_answer, unsafe_allow_html=True)
#     answer = st.text_area("It is expected to be a simple word or phrase.", key="answer", help="Enter your answer here.", placeholder="Type here...", height=10)

#     responses_submitted = 0  # Change this to the actual number of responses submitted
#     total_responses_needed = 5
    
#     if 'data' not in st.session_state:
#         st.session_state.data = []

#     if st.button("Submit"):
#         if not context_change or not selected_tags_1 or not selected_tags_2 or not question or not answer:
#             st.warning("Please fill in all fields before submitting.")
#         else:
#             entry = {
#                 'scene_id': scene_id,
#                 'question_id': f'{st.session_state.question_id:07d}',
#                 'context_change': context_change,
#                 'context_change_tags_1': selected_tags_1,
#                 'context_change_tags_2': selected_tags_2,
#                 'question': question,
#                 'answer': answer,
#             }
#             st.session_state.question_id += 1
#             st.session_state.responses_submitted += 1
#             st.session_state.data.append(entry)
#             st.success("Submitted successfully!")
            
#             with open('context_data.json', 'r') as json_file:
#                 data = json.load(json_file)
                
#             data.append(entry)
            
#             # Append the new entry to the JSON file
#             with open('context_data.json', 'w') as json_file:
#                 json.dump(data, json_file, indent=4)

#     final_section_html = f"""
#     <div style='margin-top: 20px;'>
#         <p>Please repeat <b>Step 1-3</b> for {total_responses_needed} times.</p>
#         <p>You've submitted <span style='color: red; font-weight: bold;'>{st.session_state.responses_submitted}</span> responses. Total responses needed: <span style='font-weight: bold;'>{total_responses_needed}</span>.</p>
#     </div>
#     """

#     st.markdown(final_section_html, unsafe_allow_html=True)

# else:
#     st.write("Please select a scene ID to visualize the point cloud.")


import json
import msgpack

# Load JSON data
with open('scene_annotations.json', 'r') as file:
    scene_annotations = json.load(file)

# Convert and save as MessagePack
with open('scene_annotations.msgpack', 'wb') as file:
    msgpack.pack(scene_annotations, file)