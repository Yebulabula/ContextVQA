import streamlit as st
import plotly.graph_objects as go
import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64

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
    db.collection('ContextReason').add(data)

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

@st.cache_resource
def read_instance_labels(scene_id):
    instance_labels = np.load(f'{ROOT_1}/{scene_id}/{scene_id}_instance_labels.npy')
    with open(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json', 'r') as json_file:
        id2labels = json.load(json_file)
    return instance_labels, id2labels

@st.cache_resource
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')
    
@st.cache_resource
def initialize_plot(vertices, triangles, vertex_colors, instance_labels, id2labels):
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    i, j, k = triangles[:, 0], triangles[:, 1], triangles[:, 2]

    vertex_colors_rgb = ['rgb({}, {}, {})'.format(r, g, b) for r, g, b in vertex_colors]
    
    ceiling_indices = [int(id) for id, label in id2labels.items() if 'ceiling' in label or 'wall' in label]
    mask = np.isin(instance_labels, ceiling_indices, invert=True)

    filtered_vertices = vertices[mask]
    filtered_instance_labels = instance_labels[mask]
    
    # Find good positions for category labels (using centroids of the instances)
    annotations = []
    for instance_id, label in id2labels.items():
        category = label.split('_')[0]
        if category == 'wall' or category == 'object' or category == 'floor' or category == 'ceiling':
            continue
        instance_indices = np.where(filtered_instance_labels == int(instance_id))[0]
        
        if len(instance_indices) > 0:
            instance_points = filtered_vertices[instance_indices]
            centroid = np.mean(instance_points, axis=0)
            annotations.append(dict(
                x=centroid[0],
                y=centroid[1],
                z=centroid[2],
                text=f'{category}',
                showarrow=False,
                font=dict(size=12, color='cyan'),
                xanchor='center',
            ))  
    
    trace1 = go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, vertexcolor=vertex_colors_rgb, opacity=1.0)
    fig = go.Figure(data=[trace1])
    fig.update_layout(
        scene=dict(
            aspectmode='data',
            annotations=annotations,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        width=2000,
        height=1500
    )

    return fig

# Initialize state only once
def initialize_state():
    if 'selected_label' not in st.session_state:
        st.session_state.selected_label = None

    if 'responses_submitted' not in st.session_state:
        st.session_state.responses_submitted = 0

initialize_state()

# Selectbox for scene selection
scene_id = st.selectbox("Select a Scene ID", list(SCENE_ID_TO_FILE.keys()))

if scene_id:
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    vertex_colors = vertex_colors[:, :3]

    instance_labels, id2labels = read_instance_labels(scene_id)
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

    smaller_bold_context = "<div style='font-weight: bold; font-size: 20px;'>Context Change</div>"
    smaller_bold_question = "<div style='font-weight: bold; font-size: 20px;'>Question</div>"
    smaller_bold_answer = "<div style='font-weight: bold; font-size: 20px;'>Answer</div>"

    guideline_text = """
    **Step 1:** Rotating the 3D scene and browsing the objects list on the webpage left hand side to get a basic understanding of the scene.
    
    **Step 2:** Write descriptions of context changes, create related questions, and provide concise answers.
    
    **Step 3:** Submit your responses.

    #### Context Change:
    - **Describe a possible change** that could occur in the 3D scene in one sentence.
    - Changes can be:
    - **Object Geometric Change** (e.g., object movement, rotation, shape transformation): *The backpack has been moved from the desk to the black chair.*
    - **Object Attribute Change** (e.g., color, texture, functionality, state): *The toilet paper hanging on the wall has been completely used.*
    - **Object Addition/Removal** (e.g., adding or removing objects): *The orange coach in the room is removed.*
    - Ensure the changes are feasible within the 3D scene layout, realistic, precise, and detailed.
    - **Avoid unrealistic or impossible changes**, such as "The chair is flying," or "The table becomes a spaceship," or adding objects where there is no space.
    - Classify the context change as either **local** (one object changes) or **global** (multiple objects change).

    #### Question:
    - **Write a question** that requires imagining how the scene would look after the context change.
    - The question should yield different answers before and after the change.
    - Avoid questions where the answer is obvious from the context change alone.

    #### Answer:
    - **Provide a simple word or phrase** as an answer (e.g., "Yes", "Four", "In front of the desk").
    - The answer should be directly related to the question and make sense in the context of the modified scene.

    **Good Example:**
    - Context Change: *The light switch next to the white cabinet is off.*
    - Question: *Which room becomes unusable in this situation?*
    - Answer: *Toilet.*

    **Bad Example:**
    - Context Change: *The light switch next to the white cabinet is off.*
    - Question: *What is off?*
    - Answer: *Light switch.*

    
    **Note:** Each context change can be used for multiple questions. Ensure all context changes, questions, and answers are diverse and unique. If you're stuck, try selecting a new scene—we have a total of 800 scenes available for you to choose from.


    *<span style="color:red;">Please use your imagination to its fullest. Good luck! </span>* 😁
    """


    # Display the guideline at the beginning of the page
    with st.expander("Data Collection Guidelines ", expanded=True, icon="📝"):
        st.markdown(guideline_text, unsafe_allow_html=True)


    st.markdown(smaller_bold_context, unsafe_allow_html=True, help="Write a short sentence describing the possible change may happen in the scene 3D scene. Example: ")
    context_change = st.text_area("Write a sentence to describe the possible change of the 3D scene in details.", key="context_change", placeholder="Type here...", height=10)

    tags_1 = ["Object Geometric Change", "Object Attribute Change", "Object Addition or Removal"]
    tags_2 = ["Local Change", "Global Change"]

    selected_tags_1 = st.selectbox("Select Type of Change", options=tags_1, key="selected_tags_1")
    selected_tags_2 = st.selectbox("Select Scale of Change", options=tags_2, key="selected_tags_2")

    st.markdown(smaller_bold_question, unsafe_allow_html=True)
    question = st.text_area("It is expected to be a sentence.", key="question", help="Enter your question here.", placeholder="Type here...", height=10)

    st.markdown(smaller_bold_answer, unsafe_allow_html=True)
    answer = st.text_area("It is expected to be a simple word or phrase.", key="answer", help="Enter your answer here.", height=10)

    total_responses_needed = 5

    if st.button("Submit"):
        if not context_change or not selected_tags_1 or not selected_tags_2 or not question or not answer:
            st.warning("Please fill in all fields before submitting.")
        else:
            entry = {
                'scene_id': scene_id,
                'context_change': context_change,
                'context_change_tags': [selected_tags_1, selected_tags_2],
                'question': question,
                'answer': answer,
            }
            st.session_state.responses_submitted += 1
            st.success("Submitted successfully!")
            save_context_data(entry)

    final_section_html = f"""
    <div style='margin-top: 20px;'>
        <p>You've submitted <span style='color: red; font-weight: bold;'>{st.session_state.responses_submitted}</span> responses. </span></p>
    </div>
    """
    st.markdown(final_section_html, unsafe_allow_html=True)
else:
    st.write("Please select a scene ID to visualize the point cloud.")

