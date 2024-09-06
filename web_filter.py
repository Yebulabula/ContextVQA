import streamlit as st
import plotly.graph_objects as go
import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import random
import cv2
import msgpack

firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

if firebase_credentials:
    cred_json = base64.b64decode(firebase_credentials).decode('utf-8')
    cred = credentials.Certificate(json.loads(cred_json))
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

db = firestore.client()

def save_context_data(data):
    db.collection('Filtered_Geometry').add(data)

@st.cache_data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

@st.cache_data
def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)

# Streamlit app configuration
st.set_page_config(
    page_title="ContextQA Data Collection App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ContextQA")

ROOT = "3D_scans"
SCENE_IDs = sorted(scene for scene in os.listdir(ROOT) if scene.startswith('scene'))
SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

def read_instance_labels(scene_id):
    return load_json(f'{ROOT}/{scene_id}/{scene_id}_id2labels.json')

@st.cache_resource
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

def initialize_plot(vertices, triangles, vertex_colors, annotations):
    vertex_colors_rgb = [f'rgb({r}, {g}, {b})' for r, g, b in vertex_colors[:, :3]]
    trace1 = go.Mesh3d(
        x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
        i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2],
        vertexcolor=vertex_colors_rgb, opacity=1.0
    )
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
    if 'changes' not in st.session_state:
        st.session_state.changes = load_json('movement_descriptions.json')

initialize_state()

def refresh_scene():
    scene_id = st.session_state.scene_id
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    annotations = st.session_state.annotations[scene_id]
    return initialize_plot(vertices, triangles, vertex_colors, annotations)

left_col, right_col = st.columns([2, 1])

with right_col:
    scene_id = st.selectbox("Select a Scene ID", list(SCENE_ID_TO_FILE.keys()))
    if st.session_state.scene_id != scene_id:
        st.session_state.scene_id = scene_id
        st.session_state.fig = refresh_scene()
    
    scene_id = st.session_state.scene_id
    changes = st.session_state.changes.get(scene_id, [])
    
    st.write("### Select Changes")
    selected_changes = [change for change in changes if st.checkbox(f"{change}", key=change)]

    if st.button("Submit Changes"):
        entry = {'scene_id': scene_id, 'context_change': selected_changes}
        save_context_data(entry)
        st.success("Filtered changes submitted successfully!")

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
