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
import cv2

# Initialize Firebase credentials (dummy credentials for example)
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

# Streamlit app configuration
st.set_page_config(
    page_title="ContextQA Data Collection App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ContextQA")

if firebase_credentials and not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(base64.b64decode(firebase_credentials).decode('utf-8')))
    firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

@st.cache_data(ttl=3600)  # Cache for 1 hour to avoid excessive resource use
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

@st.cache_data(ttl=3600)
def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)

# Function to save context data to Firestore (batch operation for performance)
def save_context_data(data):
    batch = db.batch()
    doc_ref = db.collection('New Answer').document()
    batch.set(doc_ref, data)
    batch.commit()

# Function to generate a confirmation code
def generate_survey_code():
    return 'CQA_' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))

@st.cache_resource(ttl=3600)  # Cached to reduce reloading for large files
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

@st.cache_data(ttl=3600)
def initialize_plot(vertices, triangles, vertex_colors, annotations):
    trace1 = go.Mesh3d(x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
                       i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2],
                       vertexcolor=vertex_colors, opacity=1.0)
    fig = go.Figure(data=[trace1])

    for annotation in annotations:
        annotation['font'] = dict(color='white', size=12)
        annotation['bgcolor'] = 'black'

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            annotations=annotations,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        width=700,
        height=1100,
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

def shuffle_page():
    """Shuffle and get a new change_description and set of questions."""
    scene_id = st.session_state.get('scene_id')
    changes = st.session_state.get('changes', {}).get(scene_id, None)

    # Use random.choice directly on keys iterator to avoid conversion to list
    change, questions = random.choice(list(changes.items()))
    
    # Update change description and questions efficiently
    st.session_state.change_questions = {change: random.sample(questions, min(4, len(questions)))}

@st.cache_data(ttl=3600)  # Reduce resource use for frequent calls
def load_data():
    annotations = load_scene_annotations()
    changes = load_json('questions/filtered_v4.json')
    answer_types = load_json('questions/0_100.json')
    return annotations, changes, answer_types

def initialize_state():
    # Initialize all data at once if not already loaded
    if 'annotations' not in st.session_state:
        st.session_state.annotations, st.session_state.changes, st.session_state.answer_types = load_data()

    if 'scene_id' not in st.session_state:
        st.session_state.scene_id = random.choice(list(st.session_state.changes.keys()))

    if 'change_questions' not in st.session_state:
        shuffle_page()

    st.session_state.survey_code = st.session_state.get('survey_code', generate_survey_code())
    st.session_state.submissions = st.session_state.get('submissions', 0)
    st.session_state.answers = st.session_state.get('answers', {})
    st.session_state.last_answer = st.session_state.get('last_answer', None)

initialize_state()

ROOT_1 = "3D_scans"
SCENE_IDs = sorted([scene for scene in st.session_state.changes.keys()])
SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_filtered_vh_clean_2.npz') for scene_id in SCENE_IDs}

@st.cache_data(ttl=3600)  # Cache with expiration to avoid excessive memory use
def read_instance_labels(scene_id):
    return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

def refresh_scene():
    scene_id = st.session_state.scene_id    
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    annotations = st.session_state.annotations[scene_id]
    st.session_state.fig = initialize_plot(vertices, triangles, vertex_colors, annotations)

if 'fig' not in st.session_state:
    refresh_scene()

@st.cache_data(ttl=3600)  # Cached to avoid loading the image multiple times
def image_to_base64(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    target_size = (900, 900)
    resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    _, encoded_image = cv2.imencode(".png", resized_image)
    return base64.b64encode(encoded_image.tobytes()).decode("utf-8")

@st.cache_data(ttl=3600)
def precompute_scene_description(scene_id):
    id2labels = read_instance_labels(scene_id)
    excluded_categories = {'wall', 'object', 'floor', 'ceiling'}
    objects_by_category = {}
    for label in id2labels.values():
        category = label.split('_')[0]
        if category not in excluded_categories:
            objects_by_category.setdefault(category, []).append(label)
    return objects_by_category

def render_markdown_block(content, bg_color, font_color="black", font_size="20px", is_bold=False):
    """Helper function to render markdown block with custom styles."""
    style = f"background-color:{bg_color}; padding:10px; border-radius:5px; margin-bottom:15px; color:{font_color}; font-size:{font_size};"
    if is_bold:
        content = f"<strong>{content}</strong>"
    return f"<div style='{style}'>{content}</div>"

def submit_response(submission):
    # Check if any answers have been provided
    if not submission['questions_and_answers']:
        st.warning("Please answer at least one question before submitting. If you're struggling, click the button below for new scene changes and questions.")
        return  # Early return to avoid further processing

    # Avoid reprocessing the same answers
    if submission['questions_and_answers'] == st.session_state.last_answer:
        st.warning("You have already answered these questions. Click the button below for a new one.")
        return  # Early return to avoid redundant state update

    # If new answers were provided, update the session state and save data
    st.session_state.submissions += 1
    st.session_state.last_answer = submission['questions_and_answers']
    save_context_data(submission)

    # Provide feedback based on the number of submissions
    if st.session_state.submissions % 4 != 0:
        st.success(f"You have processed {st.session_state.submissions} scene changes! Click the button below for the next scene change.")
        shuffle_page()
    else:
        st.success(f"Thanks for your contribution! Here is your completion code to CONNECT: {submission['survey_code']}")

@st.cache_data(ttl=3600)  # Cache for 1 hour or adjust as needed
def render_scene_change_description(change_description):
    return f"<div style='background-color:#f8d7da; padding:10px; border-radius:5px; margin-bottom:15px;'>\
            <span style='color:red; font-size:22px; font-weight:bold;'>Scene Change:</span>\
            <span style='font-size:20px;'>{change_description}</span>\
            </div>"

# Cache question rendering if the questions are static
@st.cache_data(ttl=3600)
def render_questions(questions, answer_types):
    question_blocks = []
    for question in questions:
        question_hint = answer_types.get(question, 'text').lower()
        question_block = (
            f"<div style='margin-bottom:10px;'>"
            f"<span style='color:blue; font-size:18px;'>(AFTER THE CHANGE)</span> "
            f"<span style='font-size:18px; font-weight:bold;'>{question}</span>"
            f"</div>"
            f"<div style='margin-bottom:15px;'>"
            f"<span style='color:green; font-size:18px;'>Hint: Answer should be {question_hint}</span>"
            f"</div>"
        )
        question_blocks.append(question_block)
    return question_blocks

guideline_text = """
<span style="color:brown;">**Welcome!**</span>

**Given a past 3D scene, and a hypothetical change made to the scene, you need to firstly imagine how the new scene will look like after the change happens. Then, answer a question based on the new scene. <span style="color:red;"> Do this for **4** different changes, answer one question for each of them. </span>**

The following information will be provided to help you answer the questions:
- **3D Scene Visualization**: A **past** 3D scene before the change.  <span style="color:red;">**You can rotate the scene by clicking and dragging the mouse.**</span>
- **Scene Description**: Summary of objects in the **past** scene.
- **Scene Change**: A hypothetical change made to the **past** scene.
- **Questions**: Questions about the **updated scene** in your mind after the change happens.

#### <span style="color:brown;">**(MUST READ) Instructions:**</span>
- A valid answer should be a <span style="color:red;"> **single word or phrase**</span>.
- Some questions may be confusing because they are raw data. <span style="color:red;">**You only need to choose one that you feel confident answering.**</span>
- If you find the scene change or all its questions are confusing, <span style="color:red;"> **click the button to get a new one.** </span>
- Tip 1: You can quickly locate the object by using <span style="color:red;"> **Ctrl + F** </span> and typing the object's name. 
- Tip 2: We include the answer type along with one possible answer for each question as a hint. (<span style="color:red;">**BUT DO NOT COPY THE EXAMPLE ANSWER**</span>)

#### <span style="color:brown;">**Example Scene:**</span>
<img style='display: block; margin: auto; max-width: 30%; max-height: 30%;' src='data:image/png;base64,{}'/>

- **Scene Change:** The guitar has been moved from the floor to the couch.
- **Question:** What item is directly in front of the guitar now?
- **Answer:** coffee table.

<span style="color:brown;">**You will be given a completion code after all 4 scene changes processed. Use this code to claim your reward on the Connect platform.**</span> 
"""

with st.expander("**Data Collection Guidelines --Please Read**", expanded=True, icon="📝"):
    image_path = "example1.png"
    st.markdown(guideline_text.format(image_to_base64(image_path)), unsafe_allow_html=True)

left_col, right_col = st.columns([2, 1])

with left_col:
    excluded_categories = {'wall', 'object', 'floor', 'ceiling'}
    objects_by_category = precompute_scene_description(st.session_state.scene_id)
    summary_text = "Scene Description: This scene contains " + ", ".join(
        f"{len(labels)} {category if category.endswith('s') else category + ('s' if len(labels) > 1 else '')}"
        for category, labels in objects_by_category.items() if category not in excluded_categories
    ) + "."

    st.markdown(f"\n{summary_text}")
    st.plotly_chart(st.session_state.fig, use_container_width=True)
    
with right_col:
    # Load scene data from session state only once at the beginning
    scene_id = st.session_state.get('scene_id', None)
    change_description, questions = next(iter(st.session_state.get('change_questions', {}).items()), (None, []))
    answer_types = st.session_state.get('answer_types', {})
    survey_code = st.session_state.get('survey_code', generate_survey_code())
    submissions = st.session_state.get('submissions', 0)

    submission = {
        'scene_id': scene_id,
        'change_description': change_description,
        'questions_and_answers': {},
        'survey_code': survey_code
    }

    st.markdown("""
        <style>
        div.stButton > button {
            color: red;
        }
        </style>
        """, unsafe_allow_html=True)

    # Use a form to gather inputs without page refreshes
    with st.form(key='answer_form'):
        st.markdown(render_scene_change_description(change_description), unsafe_allow_html=True)
    
        # Instructions for user
        st.markdown("<div style='background-color:#d4edda; padding:10px; border-radius:5px;'>\
                    <span style='color:black; font-size:18px;'>Choose one question you're confident answering; no need to answer all.</span>\
                    </div>", unsafe_allow_html=True)
        
        # Cached question rendering
        question_blocks = render_questions(questions, answer_types)
        
        for question_block in question_blocks:
            st.markdown(question_block, unsafe_allow_html=True)
            
            # Answer input box
            answer = st.text_area(
                label="Answer", 
                key=f"{question_block}_input", 
                placeholder="Type your answer here", 
                label_visibility="collapsed"
            )
            
            # Store the answer in the submission dictionary
            if answer:
                submission['questions_and_answers'][question_block] = answer

        # Submit button inside the form block
        submit_button = st.form_submit_button(label='Submit')

    # Handle submission outside the form
    if submit_button:
        submit_response(submission)
        
    # Separate button for getting new scene changes
    st.button('Click here to get new scene changes and questions!', on_click=shuffle_page)