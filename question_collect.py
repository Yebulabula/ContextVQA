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

firebase_credentials = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY29udGV4dHZxYSIsCiAgInByaXZhdGVfa2V5X2lkIjogIjNiMWVhOGQ5ZjBjMDJiYjEwZDQwNTI4YWFlNWFmODI0MDAzMzZlZDEiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRQ1kvdkV3QkpkN2RUcW1cblZkeHFVcExFMFFldTRFbS96dVA3YlV5YmxzUUZrVzhoNjBUUGdORlp0UXo2Z012L1VpZFBIcGxaSjRHWDVLZFhcbldVd2wrZkpHM2phZFhPcEJsaFlXaTBiNGhkWEhOY3NWSjR1dlFab0xrM05IcUJCbGhzSTU5eS96VU9QTTExc2xcbkRIVXVTL3ZhaGg4VHBwWEVubnRGV2lxNkYrTitmQmxhL3BtQlA1RDNuNG5qMnhObzgwbWsva3V3UjY0akpSZC9cbkVXeTZUaGExOXhPc3hWUFhCRUxFRXlLTGY2RzYwbU9jbnZpQWRwcU5MU2J0MUlwZUMwaWw0RlFuQUcwUUR3c3FcbmE5ay90b2t0OWs2NUFzc085dFcvVjcrTzVodmlySXUwL1pneXV3bGowbmNGRHNYb211UTRndXQ0Q3g3UUp2bndcbnA5Q3BMNTJaQWdNQkFBRUNnZ0VBRUNIdHo3amtPajNwd2NsUzlSa2c1Y1QrME9kUWozdWkyWXUwWk1HWWlOZkZcbmhxZVd1V1NsYnBhak9EVGxqZFlkVS8vdmZwR21YaHhic3QrMUlsb0JQSXpJNkgzNEs1TkdYL2t1c2h6MnBrdGJcblR5ODgwTzJUYno0TWpWVkE2VnUwMWtUazF2ekVFSUR5Mk95LzNISmhxN0N4elRJbkg3VHdYYWM4MHlPYXR1YjRcblRWMGNFYXRnVUdHQlJudjRzbVVmVG1LeU9MeFkvdWxEbllPTWtmRXlEL2lzaVlhaTBCbEY4RC9CbGlCVmJEVERcbk0veEthM21yYkh0YU0zTVVLVVdWZ1JFTFlOU0IwbWcxRGVDdldSM2RwQ1JxSUg4dWJzMGlGc0JvVG4vb0NNbUpcbkdpaHA1OGtTSlV2d2c3YWJSKzRpd2liaktrdFhEYjRrejFiNlN2MElTd0tCZ1FESlBObE8vMk12ZmtwZ1h6SDhcbmlnNW1CbGI2VWRkR29QT1pBTDdmeHpDVTd1TmtTTHJXUEVkY2gzcDNKV05tNDR6SWp0czJqd0VaZHBWdXdxTS9cbnY1Q2lwZExHMCtEMUhIL1BJK2lhUUJLWWExbHZWMHI0S2kxVWJiVFYzOVBPbkJ1S2RIZ3BRNkRhUS9tQ2RTK2hcbnkwQllXd0NJdUIzRUg1Wk5pTDY4azJHMnV3S0JnUURDb1ZnVkUvTTgrWnVpZUlUanZDSk5hNUYrakVMaXlQVlVcbitXRlBXQkpmN2tmRktuZHRleXdiZUR0U2NJRWV5OXJyVWo0anRyMCs2NDM0UTVoS2pPM2Q3c1VGRTlxcms2K09cbngrOUhtYlB6OGg3N3d2TXc3dXFncFEvZzlwUkJOZGFHS2FCMGszUWh6OFY2QXQra01sZkN6NXl0RGk5SUZ3c0RcblM3VmdqQ2E1dXdLQmdBemMyOU1GMWZRcU1WelptTnRZZzdVWHdLVjlaN0kzQlhzSkppb3RsRGhnMEo0UFhBbm5cbmpuUW1vTGhPNW55a0hOS1E5d2dVdWZCRHVTZDhQMjBLdEpjQTNHa2pEK1Q2N2x4eUlpTUI1MjVncGpYTXNaa05cbk1ScU5iSnFqRk9uRzVxZkI3QkJQSjAvc09sMlJXZnNRZjh0bC9iRy9lditYT1VjNWIxK2tXQUdUQW9HQURyTk5cbkNkcUY1cmNic0R2V0hiVmFDZXIwQkZEbnhHVlZVbU83bTlpVkdyWE9xZSs1TVlXNklTRUZxZ1poV2tnZmN1SzFcbld0RTBuZ29Bb1IzSjVPZWNGOFV2RUdFZGhSUVVrSDQ5Ym5VSGlJZGpHN1R2MVdSV1NHZnZPUmltdmY0cEE5MGxcbkIya1R2bklKQWx3eE5CK3hUVCtOSCswUVdTdVVZMTFXaDhKT01uMENnWUVBaHlYUGkxaC9MMWZybW1lWFlKTWRcblpROEhrT3dTVGdrelF6eER4WWttQ1dJN1lIeThzbU9SUGRSRlBOVEpUMVVRU0Y1d2Mwd1pENlUvTnFKMGlqTEtcblFqYzBOVUlkNmhlVFQ3cXpwdnp4VFZCcFNtbFJCVm1MTGJ3Q0plditQajczaU0rZEtSemIxYmpBQ1lEamM5OWhcbjhVazFDZW1GWXhzS2s5Z1Y0bktaQ2M4PVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLXRxc2I3QGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA1OTg2MTIxMjI3NjY5MjQ1MDM1IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay10cXNiNyU0MGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"

if firebase_credentials and not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(base64.b64decode(firebase_credentials).decode('utf-8')))
    firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

@st.cache_resource
def load_json(file_path):
    # Use mmap mode to optimize memory usage for large JSON files
    with open(file_path, 'r') as file:
        return json.load(file)

@st.cache_resource
def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)

# Function to save context data to Firestore (batch operation for performance)
def save_context_data(data):
    batch = db.batch()
    doc_ref = db.collection('Answer').document()
    batch.set(doc_ref, data)
    batch.commit()

# Function to generate a confirmation code
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

@st.cache_resource
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

@st.cache_resource
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
    """Function to shuffle and get a new change_description and questions"""
    scene_id = st.session_state.scene_id
    st.session_state.change_description = random.choice(list(st.session_state.changes[scene_id].keys()))
    st.session_state.questions = random.sample(st.session_state.changes[scene_id][st.session_state.change_description], min(5, len(st.session_state.changes[scene_id][st.session_state.change_description])))
    
def initialize_state():
    if 'annotations' not in st.session_state:
        st.session_state.annotations = load_scene_annotations()

    if 'changes' not in st.session_state:
        st.session_state.changes = load_json('questions/filtered_v4.json')
        
    if 'answer_types' not in st.session_state:
        st.session_state.answer_types = load_json('questions/0_100.json')

    if 'scene_id' not in st.session_state:
        st.session_state.scene_id = random.choice(list(st.session_state.changes.keys()))
    
    if 'change_description' not in st.session_state:
        st.session_state.change_description = random.choice(list(st.session_state.changes[st.session_state.scene_id].keys()))
        
    if 'questions' not in st.session_state:
        st.session_state.questions = random.sample(st.session_state.changes[st.session_state.scene_id][st.session_state.change_description], min(5, len(st.session_state.changes[st.session_state.scene_id][st.session_state.change_description])))
        
    if 'survey_code' not in st.session_state:
        st.session_state.survey_code = generate_survey_code()
        
    if 'submissions' not in st.session_state:
        st.session_state.submissions = []
        
    if 'answers' not in st.session_state:
        st.session_state.answers = {} 
        
initialize_state()

ROOT_1 = "3D_scans"
SCENE_IDs = sorted([scene for scene in st.session_state.changes.keys()])
SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_filtered_vh_clean_2.npz') for scene_id in SCENE_IDs}

@st.cache_resource
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

@st.cache_resource
def image_to_base64(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    target_size = (900, 900)
    resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    _, encoded_image = cv2.imencode(".png", resized_image)
    base64_image = base64.b64encode(encoded_image.tobytes()).decode("utf-8")
    return base64_image

guideline_text = """
<span style="color:brown;">**Welcome!**</span>

**Given a past 3D scene, and a hypothetical change made to the scene, you need to firstly imagine how the new scene will look like after the change happens. Then, answer a question based on the new scene. <span style="color:red;"> Do this for **5** different changes, answer at least one question for each of them. </span>**

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

<span style="color:brown;">**You will be given a completion code after all 5 scene changes processed. Use this code to claim your reward on the CloudResearch platform.**</span> 
"""

with st.expander("**Data Collection Guidelines --Please Read**", expanded=True, icon="📝"):
    image_path = "example1.png"
    st.markdown(guideline_text.format(image_to_base64(image_path)), unsafe_allow_html=True)

left_col, right_col = st.columns([2, 1])

with left_col:
    id2labels = read_instance_labels(st.session_state.scene_id)
    excluded_categories = {'wall', 'object', 'floor', 'ceiling'}
    objects_by_category = {}
    for label in id2labels.values():
        category = label.split('_')[0]
        objects_by_category.setdefault(category, []).append(label)

    summary_text = "Scene Description: This scene contains " + ", ".join(
        f"{len(labels)} {category if category.endswith('s') else category + ('s' if len(labels) > 1 else '')}"
        for category, labels in objects_by_category.items() if category not in excluded_categories
    ) + "."

    st.markdown(f"\n{summary_text}")
    st.plotly_chart(st.session_state.fig, use_container_width=True)
    
with right_col:
    submission = {
        'scene_id': st.session_state.scene_id,
        'change_description': st.session_state.change_description,
        'questions_and_answers': {},
        'survey_code': st.session_state.survey_code
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
        # Display Scene Change Description
        st.markdown(
            f"<div style='background-color:#f8d7da; padding:10px; border-radius:5px; margin-bottom:15px;'>"
            f"<span style='color:red; font-size:22px; font-weight:bold;'>Scene Change:</span> "
            f"<span style='font-size:20px;'>{st.session_state.change_description}</span>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        # Instructions for user
        st.markdown(
            "<div style='background-color:#d4edda; padding:10px; border-radius:5px;'>"
            "<span style='color:black; font-size:20px;'>Choose at least one question below to answer:</span>"
            "</div>", 
            unsafe_allow_html=True
        )
        
        answers = []
        # Loop through questions and format each question block
        for question in st.session_state.questions:
            # Question text
            st.markdown(
                f"<div style='margin-bottom:10px;'>"
                f"<span style='color:blue; font-size:18px;'>(AFTER THE CHANGE)</span> "
                f"<span style='font-size:18px; font-weight:bold;'>{question}</span>"
                f"</div>", 
                unsafe_allow_html=True
            )
            
            # Hint text
            st.markdown(
                f"<div style='margin-bottom:15px;'>"
                f"<span style='color:green; font-size:18px;'>Hint: Answer should be {st.session_state.answer_types[question].lower()}</span>"
                f"</div>", 
                unsafe_allow_html=True
            )

            # Answer input box
            st.session_state.answers[question] = st.text_area(
                label=f"Answer for {question}", 
                key=f"{question}_input", 
                placeholder="Type your answer here", 
                label_visibility="collapsed"
            )
        
        # Submit button
        submit_button = st.form_submit_button(label='Submit')

           
    if submit_button:
        submission['questions_and_answers'] = {question: st.session_state.answers[question] for question in st.session_state.questions if st.session_state.answers[question] != ''}
        if len(submission['questions_and_answers']) == 0:
            st.warning("Please answer at least one question before submitting. If you're struggling, click the button below for new scene changes and questions.")
        else:
            st.session_state.submissions.append(submission)
            save_context_data(submission)
            if len(st.session_state.submissions) % 5 != 0:
                st.success(f"You have processed {len(st.session_state.submissions)} scene changes! Click the button below for the next scene change.")
            else:
                st.success(f"Thanks for your contribution! Here is your survey code: {st.session_state.survey_code}")
                
    st.button('Click here to get new scene changes and questions!', on_click=shuffle_page)
