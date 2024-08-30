import streamlit as st
import plotly.graph_objects as go
import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import random

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
**Step 1:** Rotate the given 3D visualization and read scene descriptions to understand the 3D scene.

**Step 2:** Write descriptions of context changes, questions, concise answers.

**Step 3:** Submit your responses.

###### Context Change - Imagine a potential change that could take place in the 3D scene.
- Any realistic change in the scene is acceptable, such as moving, rotating, resizing objects, changing their color, or adding/removing items. You can also modify multiple objects simultaneously.
- Ensure your descriptions are **clear**, **detailed**, and **realistic** to avoid <span style="color:red;">rejection</span>.

###### Question - Ask a question about the 'modified' scene only, rather than compare it with the 'original' scene.
- Your questions shouldn't be answered solely by reading the context change without viewing the scene.
- Your questions should yield a different answer when your context change is applied to the scene.
- Your questions shouldn't have **multiple**, **ambiguous**, **subjective**, or **yes/no** answers.

###### Answer - Give a simple, concise answer that is unique to the question and fits the modified scene.

<span style="color:red;"> **Good example:** </span> 
- **Context Change:** The white nightstand next to the coffee table and the room’s only trash can have swapped positions. **Q:** What is located between the two beds in the room?
**A:** Yellow Chair.
- **Context Change:** A new chair has been placed around the round table. **Q:** How many chairs are now to the left of the desk? **A:** Three.
- **Context Change:** The toilet paper hanging on the wall has been completely used. **Q:** Where is the other toilet paper roll? **A:** On top of the toilet's water tank.

<span style="color:green;"> **Bad example:** </span> 

- **Context Change:** Several trash cans are added. (*Ambiguous*) **Q:** What is the color of the trash can? (*Unrelated to the context change*) **A:** After carefully examining the scene, the color of the trash can is blue. (*Too long*)
- **Context Change:** The microwave has been moved from under the cabinet to on the kitchen counter into the corner. **Q:** Is the microwave now closer to the refrigerator in its new spot? (*Yes/No question, comparing the original scene*) **A:** No.

**Trick:** It's best to consider a meaningful context change that allows you to ask multiple questions, so you won't need to rewrite the context changes each time. If you're stuck, refresh the page to get a new scene. 

*<span style="color:red;">Please use your imagination to its fullest. Good luck!</span>* 😁
"""

# Display the guideline at the beginning of the form
with st.expander("**Data Collection Guidelines --Please Read**", expanded=True, icon="📝"):
    st.markdown(guideline_text, unsafe_allow_html=True)

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

    smaller_bold_context = "<div style='font-weight: bold; font-size: 20px;'>Context Change</div>"
    smaller_bold_question = "<div style='font-weight: bold; font-size: 20px;'>Question</div>"
    smaller_bold_answer = "<div style='font-weight: bold; font-size: 20px;'>Answer</div>"

    st.markdown(smaller_bold_context, unsafe_allow_html=True)
    context_change = st.text_area("Describe any changes that could reasonably occur in the scene.", key="context_change", placeholder="Type here...", height=10)
    
    if st.button("Click here to view some example context changes."):
        st.info(random.choice(context_inspirations))
    
    st.markdown(smaller_bold_question, unsafe_allow_html=True)
    question = st.text_area("Ask a question to the 'imagined' scene, rather than the 'original scene'.", key="question", placeholder="Type here...", height=10)

    if st.button("Click here to view some example questions."):
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
    

