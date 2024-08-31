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

SCENE_IDs = sorted([scene for scene in os.listdir(ROOT_1) if scene.startswith('scene')])

SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

question_inspirations = json.load(open('question_inspirations.json'))

context_inspirations = json.load(open('context_inspirations.json'))

scene_annotations = json.load(open('scene_annotations.json'))

# Cached function to read instance labels
@st.cache_data
def read_instance_labels(scene_id):
    instance_labels = np.load(f'{ROOT_1}/{scene_id}/{scene_id}_instance_labels.npy')
    with open(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json', 'r') as json_file:
        id2labels = json.load(json_file)
    return instance_labels, id2labels

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

    
    fig.update_layout(
        scene=dict(
            aspectmode='data',
            annotations=annotations,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        width=900,
        height=700,
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
        
    if 'scene_id' not in st.session_state:
        st.session_state.scene_id = None

initialize_state()

guideline_text = """
<span style="color:brown;">**Welcome!**</span> 

To complete this task, you need to firstly understand the given 3D scene. Then, think of a hypothetical change the scene  you can make to the scene and write it down.  After that, imagine what the scene looks like with the change and ask a question about the 'changed' scene. Finally, give a concise answer to your question.

###### Hypothetical Scene Change
- Imagine a change that could happen in the scene. This is just pretend, so you don't need to actually change anything in the scene. You can think of moving, rotating, resizing, or changing the color, state, function, adding, or removing **one or more objects**—any realistic change is acceptable.
- The change decription should be **clear**, **detailed**, and **realistic** to avoid <span style="color:red;">**rejection**</span>.

###### Question - Ask a question about the scene following the hypothetical change.
- Your questions shouldn't be answered solely by reading the Scene Change without viewing the scene.
- Your questions shouldn't give the same answer, no matter whether the scene change happened.
- Your questions shouldn't have **multiple**, **ambiguous**, **subjective**, or **yes/no** answers to avoid <span style="color:red;">**rejection**</span>.

###### Answer - Provide a simple word or phrase as an <span style="color:red;"> **unique** </span>  answer to your question.

**Example:**

This scene contains 2 windows, 2 tables, 1 kitchen counter, 1 shower, 2 curtains, 1 desk, 5 cabinets, 1 sink, 1 scale, 3 trash cans, 1 tv, 1 pillow, 1 clock, 1 backpack, 4 stools, 1 couch, 1 refrigerator, 1 coffee table, 1 toilet, 1 bed, 2 kitchen cabinetss, 1 toaster oven, 1 laundry basket, <span style="color:red;">**1 guitar**</span>, 1 tissue box, 2 nightstands, 1 dish rack, 1 microwave, 1 toaster, 1 door, 1 shelf, 1 bicycle, 1 shoes, 2 doorframes, 1 mirror, 1 guitar case.

<img style='display: block; margin: auto; max-width: 30%; max-height: 30%;' src='data:image/png;base64,{}'/>

- <span style="color:red;"> **Good:** </span> **Scene Change:** There are two new guitars has been leaned against the refrigerator. **Q:**  How many guitars in this room now? **Answer:** Three.
- <span style="color:red;"> **Good:** </span> **Scene Change:** The brown pillow that was on the bed has been moved to the gray couch. **Q:**  What is the closest item in front of the pillow now? **Answer:** Coffee table.
- <span style="color:red;"> **Good:** </span> **Scene Change:** The coffee table has been changed to match the color of the bed. **Q:** What is the color of the coffee table? **Answer:** Blue.
- <span style="color:green;">**Bad:**</span> **Scene Change:** The brown pillow that was on the bed has been moved to the gray couch. **Q:** What color is the pillow? **A:** Brown.
(**The pillow color is not affected by the scene change**)
 
- <span style="color:green;">**Bad:**</span> **Scene Change:** The brown pillow that was on the bed has been moved to the gray couch. **Q:** What is on the gray couch now? **A:** Pillow. (**The question can be answered by only reading the scene change**) 

**Trick:** Pick a Scene Change that lets you ask more than one question, so you don't have to make a new change each time. If you're stuck, refresh the page for a new scene.

*We do have some templates to inspire you. But these templates are not related to the scene you are looking at. You should not copy them.*

*<span style="color:red;">Please use your imagination to its fullest. Good luck!</span>* 😁
"""

@st.cache_resource
def render_img_html(image_b64):
    st.markdown(f"<img style='max-width: 40%;max-height: 40%;' src='data:image/png;base64, {image_b64}'/>", unsafe_allow_html=True)

@st.cache_resource
def image_to_base64(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    target_size = (600, 600)  # Adjust the size to your needs
    resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    
    _, encoded_image = cv2.imencode(".png", resized_image)
    base64_image = base64.b64encode(encoded_image.tobytes()).decode("utf-8")
    return base64_image

# Display the guideline at the beginning of the form
with st.expander("**Data Collection Guidelines --Please Read**", expanded=True, icon="📝"):
    image_path = "scene0000_00.png"
    st.markdown(guideline_text.format(image_to_base64(image_path)), unsafe_allow_html=True)

# Randomly select a scene ID when the page loads

left_col, right_col = st.columns([2, 1])

# Right column: Form
with right_col:
    if not st.session_state.scene_id:
        random_scene_id = random.choice(list(SCENE_ID_TO_FILE.keys()))
        st.session_state.scene_id = random_scene_id
    else:
        random_scene_id = st.session_state.scene_id
        
    scene_id = random_scene_id  # Use the randomly selected scene ID

    smaller_bold_context = "<div style='font-weight: bold; font-size: 20px;'>Scene Change</div>"
    smaller_bold_question = "<div style='font-weight: bold; font-size: 20px;'>Question</div>"
    smaller_bold_answer = "<div style='font-weight: bold; font-size: 20px;'>Answer</div>"

    st.markdown(smaller_bold_context, unsafe_allow_html=True)
    context_change = st.text_area("Imagine a change that is reasonably happen in the given 3D scene.", key="context_change", placeholder="Type here...", height=10)
    
    if st.button("Click here to view some Scene Change templates (Do not copy it)."):
        st.info(random.choice(context_inspirations))
    
    st.markdown(smaller_bold_question, unsafe_allow_html=True)
    question = st.text_area("Imagine the scene after change, then ask a question.", key="question", placeholder="Type here...", height=10)

    if st.button("Click here to view some question templates (Do not copy it)."):
        st.info(random.choice(question_inspirations))
    
    st.markdown(smaller_bold_answer, unsafe_allow_html=True)
    answer = st.text_area("Answer has to be a simple word or a phrase.", key="answer", placeholder="Type here...", height=10)

    total_responses_needed = 5

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

            # Check if the entry already exists in the Firestore
            duplicates_query = db.collection('ContextReason').where('scene_id', '==', scene_id) \
                                                .where('context_change', '==', context_change) \
                                                .where('question', '==', question) \
                                                .where('answer', '==', answer) \
                                                .stream()

            # Convert the query results to a list
            duplicates = list(duplicates_query)

            if duplicates:
                st.warning("This submission has already been made. Please do not submit duplicate entries.")
            else:
                # Increment the responses submitted count
                st.session_state.responses_submitted += 1
                save_context_data(entry)
                
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

    instance_labels, id2labels = read_instance_labels(scene_id)
    id2labels = {int(k): v for k, v in id2labels.items()}

    annotations = scene_annotations[scene_id]
    
    initialize_plot(vertices, triangles, vertex_colors, annotations, id2labels)
    

