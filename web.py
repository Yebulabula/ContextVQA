import streamlit as st
import plotly.graph_objects as go
import os
import numpy as np
import json
from plyfile import PlyData

# Streamlit app
st.set_page_config(
    page_title="ContextQA Data Collection App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
st.title("ContextQA")

ROOT_1 = "3D_scans"
SCENE_IDs = sorted(os.listdir(ROOT_1))
SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

@st.cache_data
def read_instance_labels(scene_id, dataset='scannet'):
    instance_labels = np.load(f'{ROOT_1}/{scene_id}/{scene_id}_instance_labels.npy')
    with open(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json', 'r') as json_file:
        id2labels = json.load(json_file)
    return instance_labels, id2labels

@st.cache_data
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

@st.cache_data
def initialize_plot(vertices, triangles, vertex_colors, instance_labels, id2labels):
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    i, j, k = triangles[:, 0], triangles[:, 1], triangles[:, 2]

    vertex_colors_rgb = ['rgb({}, {}, {})'.format(r, g, b) for r, g, b in vertex_colors]

    trace1 = go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        vertexcolor=vertex_colors_rgb,
        opacity=1.0
    )

    fig = go.Figure(data=[trace1])
    fig.update_layout(scene=dict(aspectmode='data'),
                      width=2000,
                      height=1500)

    return fig

def get_semantic_category_counts(instance_labels, id2labels):
    category_counts = {}
    for instance_id in np.unique(instance_labels):
        if instance_id == -100:
            continue
        label = id2labels.get(instance_id, 'Unknown')
        category = label.split('_')[0]
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1
    return category_counts

# Load context data from JSON
def load_context_data():
    if not os.path.exists('context_data.json'):
        with open('context_data.json', 'w') as json_file:
            json_file.write(json.dumps([]))
    with open('context_data.json', 'r') as json_file:
        return json.load(json_file)

def save_context_data(data):
    with open('context_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

data = load_context_data()

# State initialization
if 'selected_label' not in st.session_state:
    st.session_state.selected_label = None

if 'data' not in st.session_state:
    st.session_state.data = []

if 'responses_submitted' not in st.session_state:
    st.session_state.responses_submitted = 0

if 'question_id' not in st.session_state:
    st.session_state.question_id = int(data[-1]['question_id']) + 1 if data else 0

# Selectbox for scene selection
scene_id = st.selectbox("Select a Scene ID", list(SCENE_ID_TO_FILE.keys()))

if scene_id:
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    vertex_colors = vertex_colors[:, :3]

    instance_labels, id2labels = read_instance_labels(scene_id, 'scannet' if scene_id.startswith('scene') else '3rscan')
    labels2id = {v: int(k) for k, v in id2labels.items()}
    id2labels = {int(k): v for k, v in id2labels.items()}

    if 'fig' not in st.session_state or st.session_state.get('scene_id') != scene_id:
        st.session_state.fig = initialize_plot(vertices, triangles, vertex_colors, instance_labels, id2labels)
        st.session_state.scene_id = scene_id

    st.markdown(
        """
        <style>
        .label-entry {
            background-color: #007bff;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .label-entry.selected {
            background-color: red;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<h2 class="scene-title">3D Scene Visualization</h2>', unsafe_allow_html=True)

    st.plotly_chart(st.session_state.fig, use_container_width=True)

    # Sidebar object listing
    st.sidebar.header("List of objects")
    objects_by_category = {}
    for instance_id, label in id2labels.items():
        category = label.split('_')[0]
        if category not in objects_by_category:
            objects_by_category[category] = []
        objects_by_category[category].append(label)

    for category, labels in objects_by_category.items():
        expander_label = f"{category.capitalize()} | Amount: {len(labels)}"
        with st.sidebar.expander(expander_label):
            for label in labels:
                if st.button(label, key=label):
                    st.session_state.selected_label = label if st.session_state.selected_label != label else None

    smaller_bold_context = "<div style='font-weight: bold; font-size: 20px;'>Step 1: Context Change</div>"
    smaller_bold_question = "<div style='font-weight: bold; font-size: 20px;'>Step 2: Question</div>"
    smaller_bold_answer = "<div style='font-weight: bold; font-size: 20px;'>Step 3: Answer</div>"

    st.markdown(smaller_bold_context, unsafe_allow_html=True, help="Write a short sentence describing the change of the 3D scene.")
    context_change = st.text_area("Write a short sentence describing the change of the 3D scene.", key="context_change", help="Enter context change details here.", placeholder="Type here...", height=10)

    tags_1 = ["Object Geometric Change", "Object Attribute Change", "Object Addition or Removal"]
    tags_2 = ["Local Change", "Global Change"]

    selected_tags_1 = st.selectbox("Select Type of Change", options=tags_1, key="selected_tags_1")
    selected_tags_2 = st.selectbox("Select Scale of Change", options=tags_2, key="selected_tags_2")

    st.markdown(smaller_bold_question, unsafe_allow_html=True)
    question = st.text_area("It is expected to be a sentence.", key="question", help="Enter your question here.", placeholder="Type here...", height=10)

    st.markdown(smaller_bold_answer, unsafe_allow_html=True)
    answer = st.text_area("It is expected to be a simple word or phrase.", key="answer", help="Enter your answer here.", placeholder="Type here...", height=10)

    total_responses_needed = 5

    if st.button("Submit"):
        if not context_change or not selected_tags_1 or not selected_tags_2 or not question or not answer:
            st.warning("Please fill in all fields before submitting.")
        else:
            entry = {
                'scene_id': scene_id,
                'question_id': f'{st.session_state.question_id:07d}',
                'context_change': context_change,
                'context_change_tags_1': selected_tags_1,
                'context_change_tags_2': selected_tags_2,
                'question': question,
                'answer': answer,
            }
            st.session_state.question_id += 1
            st.session_state.responses_submitted += 1
            st.session_state.data.append(entry)
            st.success("Submitted successfully!")

            data.append(entry)
            save_context_data(data)

    final_section_html = f"""
    <div style='margin-top: 20px;'>
        <p>Please repeat <b>Step 1-3</b> for {total_responses_needed} times.</p>
        <p>You've submitted <span style='color: red; font-weight: bold;'>{st.session_state.responses_submitted}</span> responses. Total responses needed: <span style='font-weight: bold;'>{total_responses_needed}</span>.</p>
    </div>
    """
    st.markdown(final_section_html, unsafe_allow_html=True)
else:
    st.write("Please select a scene ID to visualize the point cloud.")
