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

# Initialize Firebase credentials (dummy credentials for example)
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

if firebase_credentials:
    if not firebase_admin._apps:
        cred = credentials.Certificate(json.loads(base64.b64decode(firebase_credentials).decode('utf-8')))
        firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

@st.cache_data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
@st.cache_data
def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)
    
# Function to save context data to Firestore
def save_context_data(data):
    db.collection('ContextChanges').add(data)

# Function to generate and return a confirmation code
def generate_survey_code():
    return 'CQA_' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))

# Streamlit app configuration
st.set_page_config(
    page_title="ContextQA Data Collection App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ContextQA")

ROOT_1 = "3D_scans"
# Get sorted scene IDs that start with 'scene'
scene_ids = sorted([scene for scene in os.listdir(ROOT_1) if scene.startswith('scene')])

# Get sorted rscans that do not start with 'scene', limited to the first 200
rscans = sorted([scene for scene in os.listdir(ROOT_1) if not scene.startswith('scene')])[:200]

# Combine scene_ids and rscans
SCENE_IDs = scene_ids + rscans

SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

def read_instance_labels(scene_id):
    return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

@st.cache_resource
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

def initialize_plot(vertices, triangles, vertex_colors, annotations):
    vertex_colors_rgb = [f'rgb({r}, {g}, {b})' for r, g, b in vertex_colors[:, :3]]

    trace1 = go.Mesh3d(x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2], i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2], vertexcolor=vertex_colors_rgb, opacity=1.0)
    fig = go.Figure(data=[trace1])

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            annotations=annotations,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        width=900,
        height=900,
        margin=dict(l=0, r=10, b=0, t=20),
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
    
    return fig

def initialize_state():
    if 'scene_id' not in st.session_state:
        st.session_state.scene_id = None

    if 'annotations' not in st.session_state:
        st.session_state.annotations = load_scene_annotations()
        
    if 'survey_code' not in st.session_state:
        st.session_state.survey_code = generate_survey_code()
        
initialize_state()

def refresh_scene():
    st.session_state.scene_id = random.choice(list(SCENE_ID_TO_FILE.keys()))
    scene_id = st.session_state.scene_id
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    
    annotations = st.session_state.annotations[scene_id]
    return initialize_plot(vertices, triangles, vertex_colors, annotations)

guideline_text = """
<span style="color:brown;">**Welcome!**</span> 

First, look at the 3D scene and think about how you could change the objects in it. Then, describe five different changes. Follow these rules:

1. Any change that fits naturally within the scene's layout and context is acceptable. For example, you might consider:
- Moving objects in the scene. 
- Changing visual appearance of object(s) (e.g., changing object color).
- Altering the functionality or state of objects(s) (e.g., open/close a fridge door).
- Adding, removing, or replacing objects within the scene.
- ... and more!
2. You can change one or more objects in the scene. 
3. Provide a detailed description of the change, specifying exactly which object(s) are changed and how they are changed. Vague or brief descriptions will be <span style="color:red;">rejected</span>.
4. Ensure the five changes are unique in type and applied to different objects. Repetitive changes will be <span style="color:red;">rejected</span>, while diverse changes may receive a <span style="color:green;">bonus</span>.

Examples:
- *The black jacket that was next to the couch has been placed in the laundry basket.*
- *A coffee machine is added on the kitchen counter next to the toaster oven for added convenience.*

Note: To maintain data quality, we encourage you to make complex and diverse changes that are neither too simple nor too similar. After submitting your changes, you'll receive a completion code. Be sure to save this code and submit it to CloudResearch to receive your payment.

**If you find your scene too simple, you can refresh the page to load a new one. However, make sure all your changes are based on the same scene.**

*<span style="color:red;"> Feel free to unleash your creativity to the fullest! Best of luck!</span>* 😁
"""

with st.expander("**Data Collection Guidelines --Please Read**", expanded=True, icon="📝"):
    st.markdown(guideline_text, unsafe_allow_html=True)

left_col, right_col = st.columns([2, 1])

with right_col:
    scene_id = st.session_state.scene_id

    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Scene Change 1</div>", unsafe_allow_html=True)
    context_change = st.text_area("Imagine a change that is reasonably happen in the given 3D scene.", key="change1", placeholder="Type here...", height=10)
    
    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Scene Change 2</div>", unsafe_allow_html=True)
    context_change = st.text_area("Imagine a change that is reasonably happen in the given 3D scene.", key="change2", placeholder="Type here...", height=10)
    
    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Scene Change 3</div>", unsafe_allow_html=True)
    context_change = st.text_area("Imagine a change that is reasonably happen in the given 3D scene.", key="change3", placeholder="Type here...", height=10)
    
    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Scene Change 4</div>", unsafe_allow_html=True)
    context_change = st.text_area("Imagine a change that is reasonably happen in the given 3D scene.", key="change4", placeholder="Type here...", height=10)
    
    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Scene Change 5</div>", unsafe_allow_html=True)
    context_change = st.text_area("Imagine a change that is reasonably happen in the given 3D scene.", key="change5", placeholder="Type here...", height=10)

    if st.button("Submit"):
        # Extract changes using list comprehension
        changes = [st.session_state.get(f'change{i}') for i in range(1, 6)]
        
        # Check if all changes are unique and non-empty
        if len(set(changes)) < len(changes):
            st.warning("Please ensure that all changes are unique.")
        elif not all(changes):
            st.warning("Please fill in all the changes.")
        else:
            # Proceed with success case
            st.session_state.survey_code = generate_survey_code()
            st.success(f"Congratulations! Your Completion Code is: {st.session_state.survey_code}. Please submit this code to CloudResearch.")
            
            # Prepare entry for saving
            entry = {
                'scene_id': scene_id,
                'changes': changes,
                'survey_code': st.session_state.survey_code
            }
            save_context_data(entry)

with left_col:
    if 'fig' not in st.session_state:
        st.session_state.fig = refresh_scene()
    
    id2labels = read_instance_labels(st.session_state.scene_id)
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
    
    st.plotly_chart(st.session_state.fig, use_container_width=True)
