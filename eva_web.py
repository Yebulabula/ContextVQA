import streamlit as st
import plotly.graph_objects as go
import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import random
import msgpack


firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

if firebase_credentials:
    # Decode the base64 encoded credentials
    cred_json = base64.b64decode(firebase_credentials).decode('utf-8')
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)

    # Initialize Firebase app if not already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

# Function to save context data to Firestore
def save_context_data(data):
    db.collection('EvaContext').add(data)

# Streamlit app configuration
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

SCENE_IDs = sorted(os.listdir(ROOT_1), key=lambda x: (not x.startswith('scene'), x))

SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

@st.cache_data
def get_scene_ids_and_files(root_dir):
    scene_ids = sorted(os.listdir(root_dir), key=lambda x: (not x.startswith('scene'), x))
    return {scene_id: os.path.join(root_dir, scene_id, f'{scene_id}_filtered_vh_clean_2.npz') for scene_id in scene_ids}

SCENE_ID_TO_FILE = get_scene_ids_and_files(ROOT_1)

@st.cache_data
def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)
scene_annotations = load_scene_annotations()
# Cached function to read instance labels

@st.cache_data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

@st.cache_data
def read_instance_labels(scene_id):
    return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

def generate_survey_code():
    return 'CQA_' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))

# Cached function to load mesh data with memory mapping
@st.cache_resource
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

# Function to initialize the plot and create annotations
def initialize_plot(vertices, triangles, vertex_colors, annotations, id2labels):
    vertex_colors_rgb = [f'rgb({r}, {g}, {b})' for r, g, b in vertex_colors]

    excluded_categories = {'wall', 'object', 'floor', 'ceiling'}

    objects_by_category = {}
    for label in id2labels.values():
        category = label.split('_')[0]
        objects_by_category.setdefault(category, []).append(label)

    summary_text = "This scene contains " + ", ".join(
        f"{len(labels)} {category + ('s' if len(labels) > 1 else '')}"
        for category, labels in objects_by_category.items() if category not in excluded_categories
    ) + "."

    st.markdown(f"\n{summary_text}")
    trace1 = go.Mesh3d(x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2], i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2], vertexcolor=vertex_colors_rgb, opacity=1.0)
    fig = go.Figure(data=[trace1])

    for annotation in annotations:
        annotation['font'] = dict(color='white', size=10)  # Set font to white
        annotation['bgcolor'] = 'black'  # Add a black background for contrast
        
    fig.update_layout(
        scene=dict(
            aspectmode='data',
            annotations=annotations,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        width=1000,
        height=800,
        margin=dict(l=0, r=10, b=0, t=10),
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                buttons=[
                    dict(args=["scene.annotations", annotations], label="Show Object Names", method="relayout"),
                    dict(args=["scene.annotations", []], label="Hide Object Names", method="relayout")
                ],
                showactive=True,
                xanchor="left",
                yanchor="top"
            ),
        ]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    return fig

# Initialize state only once
def initialize_state():
    if 'selected_label' not in st.session_state:
        st.session_state.selected_label = None

    if 'responses_submitted' not in st.session_state:
        st.session_state.responses_submitted = 0

initialize_state()
                
left_col, right_col = st.columns([2, 1])


# Right column: Form
with right_col:
    scene_id = st.selectbox("Select a Scene ID", list(SCENE_ID_TO_FILE.keys()))

    smaller_bold_context = "<div style='font-weight: bold; font-size: 20px;'>Context Change</div>"
    smaller_bold_question = "<div style='font-weight: bold; font-size: 20px;'>Question</div>"
    smaller_bold_answer = "<div style='font-weight: bold; font-size: 20px;'>Answer</div>"

    st.markdown(smaller_bold_context, unsafe_allow_html=True)
    context_change = st.text_area("Describe any changes that could reasonably occur in the scene.", key="context_change", placeholder="Type here...", height=10)
    

    st.markdown(smaller_bold_question, unsafe_allow_html=True)
    question = st.text_area("Write a question related to the context change.", key="question", placeholder="Type here...", height=10)

    st.markdown(smaller_bold_answer, unsafe_allow_html=True)
    answer = st.text_area("Answer has to be a simple word or a phrase.", key="answer", placeholder="Type here...", height=10)

    if st.button("Submit"):
        if not context_change or not question or not answer:
            st.warning("Please fill in all fields before submitting.")
        else:
            entry = {
                'scene_id': scene_id,
                'context_change': context_change,
                'question': question,
                'answer': answer,
            }

            survey_code = generate_survey_code()
            st.success(f"Congratulations! You have successfully completed the task. Here is your Completion Code: {survey_code}")
            
            # Save the entry with the survey code
            entry['survey_code'] = survey_code
            save_context_data(entry)
    
with left_col:
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    vertex_colors = vertex_colors[:, :3]

    id2labels = read_instance_labels(scene_id)

    annotations = scene_annotations[scene_id]
    
    initialize_plot(vertices, triangles, vertex_colors, annotations, id2labels)