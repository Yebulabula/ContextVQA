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

# firebase_credentials="ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY29udGV4dHZxYSIsCiAgInByaXZhdGVfa2V5X2lkIjogIjNiMWVhOGQ5ZjBjMDJiYjEwZDQwNTI4YWFlNWFmODI0MDAzMzZlZDEiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRQ1kvdkV3QkpkN2RUcW1cblZkeHFVcExFMFFldTRFbS96dVA3YlV5YmxzUUZrVzhoNjBUUGdORlp0UXo2Z012L1VpZFBIcGxaSjRHWDVLZFhcbldVd2wrZkpHM2phZFhPcEJsaFlXaTBiNGhkWEhOY3NWSjR1dlFab0xrM05IcUJCbGhzSTU5eS96VU9QTTExc2xcbkRIVXVTL3ZhaGg4VHBwWEVubnRGV2lxNkYrTitmQmxhL3BtQlA1RDNuNG5qMnhObzgwbWsva3V3UjY0akpSZC9cbkVXeTZUaGExOXhPc3hWUFhCRUxFRXlLTGY2RzYwbU9jbnZpQWRwcU5MU2J0MUlwZUMwaWw0RlFuQUcwUUR3c3FcbmE5ay90b2t0OWs2NUFzc085dFcvVjcrTzVodmlySXUwL1pneXV3bGowbmNGRHNYb211UTRndXQ0Q3g3UUp2bndcbnA5Q3BMNTJaQWdNQkFBRUNnZ0VBRUNIdHo3amtPajNwd2NsUzlSa2c1Y1QrME9kUWozdWkyWXUwWk1HWWlOZkZcbmhxZVd1V1NsYnBhak9EVGxqZFlkVS8vdmZwR21YaHhic3QrMUlsb0JQSXpJNkgzNEs1TkdYL2t1c2h6MnBrdGJcblR5ODgwTzJUYno0TWpWVkE2VnUwMWtUazF2ekVFSUR5Mk95LzNISmhxN0N4elRJbkg3VHdYYWM4MHlPYXR1YjRcblRWMGNFYXRnVUdHQlJudjRzbVVmVG1LeU9MeFkvdWxEbllPTWtmRXlEL2lzaVlhaTBCbEY4RC9CbGlCVmJEVERcbk0veEthM21yYkh0YU0zTVVLVVdWZ1JFTFlOU0IwbWcxRGVDdldSM2RwQ1JxSUg4dWJzMGlGc0JvVG4vb0NNbUpcbkdpaHA1OGtTSlV2d2c3YWJSKzRpd2liaktrdFhEYjRrejFiNlN2MElTd0tCZ1FESlBObE8vMk12ZmtwZ1h6SDhcbmlnNW1CbGI2VWRkR29QT1pBTDdmeHpDVTd1TmtTTHJXUEVkY2gzcDNKV05tNDR6SWp0czJqd0VaZHBWdXdxTS9cbnY1Q2lwZExHMCtEMUhIL1BJK2lhUUJLWWExbHZWMHI0S2kxVWJiVFYzOVBPbkJ1S2RIZ3BRNkRhUS9tQ2RTK2hcbnkwQllXd0NJdUIzRUg1Wk5pTDY4azJHMnV3S0JnUURDb1ZnVkUvTTgrWnVpZUlUanZDSk5hNUYrakVMaXlQVlVcbitXRlBXQkpmN2tmRktuZHRleXdiZUR0U2NJRWV5OXJyVWo0anRyMCs2NDM0UTVoS2pPM2Q3c1VGRTlxcms2K09cbngrOUhtYlB6OGg3N3d2TXc3dXFncFEvZzlwUkJOZGFHS2FCMGszUWh6OFY2QXQra01sZkN6NXl0RGk5SUZ3c0RcblM3VmdqQ2E1dXdLQmdBemMyOU1GMWZRcU1WelptTnRZZzdVWHdLVjlaN0kzQlhzSkppb3RsRGhnMEo0UFhBbm5cbmpuUW1vTGhPNW55a0hOS1E5d2dVdWZCRHVTZDhQMjBLdEpjQTNHa2pEK1Q2N2x4eUlpTUI1MjVncGpYTXNaa05cbk1ScU5iSnFqRk9uRzVxZkI3QkJQSjAvc09sMlJXZnNRZjh0bC9iRy9lditYT1VjNWIxK2tXQUdUQW9HQURyTk5cbkNkcUY1cmNic0R2V0hiVmFDZXIwQkZEbnhHVlZVbU83bTlpVkdyWE9xZSs1TVlXNklTRUZxZ1poV2tnZmN1SzFcbld0RTBuZ29Bb1IzSjVPZWNGOFV2RUdFZGhSUVVrSDQ5Ym5VSGlJZGpHN1R2MVdSV1NHZnZPUmltdmY0cEE5MGxcbkIya1R2bklKQWx3eE5CK3hUVCtOSCswUVdTdVVZMTFXaDhKT01uMENnWUVBaHlYUGkxaC9MMWZybW1lWFlKTWRcblpROEhrT3dTVGdrelF6eER4WWttQ1dJN1lIeThzbU9SUGRSRlBOVEpUMVVRU0Y1d2Mwd1pENlUvTnFKMGlqTEtcblFqYzBOVUlkNmhlVFQ3cXpwdnp4VFZCcFNtbFJCVm1MTGJ3Q0plditQajczaU0rZEtSemIxYmpBQ1lEamM5OWhcbjhVazFDZW1GWXhzS2s5Z1Y0bktaQ2M4PVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLXRxc2I3QGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA1OTg2MTIxMjI3NjY5MjQ1MDM1IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay10cXNiNyU0MGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"


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
    db.collection('Question_Answer').add(data)

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

# @st.cache_resource
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

def initialize_plot(vertices, triangles, vertex_colors, annotations):
    trace1 = go.Mesh3d(x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2], i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2], vertexcolor=vertex_colors, opacity=1.0)
    fig = go.Figure(data=[trace1])

    for annotation in annotations:
        annotation['font'] = dict(color='white', size=12)  # Set font to white
        annotation['bgcolor'] = 'black'  # Add a black background for contrast
    
    fig.update_layout(
        scene=dict(
            aspectmode='data',
            annotations=annotations,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        width=800,
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
        
    if 'change_description' not in st.session_state:
        st.session_state.change_description = None

    if 'annotations' not in st.session_state:
        st.session_state.annotations = load_scene_annotations()
        
        
    if 'changes' not in st.session_state:
        st.session_state.changes = load_json('context_changes_human/final_total_change.json')
        
    if 'survey_code' not in st.session_state:
        st.session_state.survey_code = generate_survey_code()

initialize_state()

ROOT_1 = "3D_scans"
# Get sorted scene IDs that start with 'scene'
SCENE_IDs = sorted([scene for scene in st.session_state.changes.keys()])

SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_filtered_vh_clean_2.npz') for scene_id in SCENE_IDs}

def read_instance_labels(scene_id):
    return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

def refresh_scene():
    st.session_state.scene_id = random.choice(list(SCENE_ID_TO_FILE.keys()))
    scene_id = st.session_state.scene_id
    st.session_state.change_description = random.sample(st.session_state.changes[scene_id], 4)
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    
    annotations = st.session_state.annotations[scene_id]
    return initialize_plot(vertices, triangles, vertex_colors, annotations)

guideline_text = """
<span style="color:brown;">**Welcome!**</span>

Begin with a past 3D scene visualization and a description of a hypothetical change. First, imagine how the scene appears after the change. Then, come up with four unique questions about the altered scene in your mind and provide answers for each one.

<span style="color:brown;">**Instructions:**</span>

<span style="color:brown;">- The answer to each question must rely on both the knowledge of the original 3D scene visualization and the description of the change. Answers based solely on one will be rejected.</span>

<span style="color:brown;">- All questions should be realistic and must have a unique answer.</span>

<span style="color:brown;">- Each question must be at least 8 words long.</span>

<span style="color:brown;">- The answer should be a single word or a short phrase.</span>

**Consider the example scene below. Possible movements can include: (*This is just an example; please do not use it to write questions.*)**

<span style="color:brown;">**Scene Change:** The brown pillow, originally on the bed, has been moved to the gray couch.</span>

- **Good Question:** What object is in front of the pillow now?  
  **Answer:** Coffee table.
  
- <span style="color:green;">**Bad Question:** Is there a pillow on the couch now?  
  **Answer:** Yes.  
  (*This question can be answered by the change description alone.*)</span>

<span style="color:brown;">**Scene Change:** The shoes next to the white table have been removed.</span>

- **Good Question:** What is the only remaining object leaning against the curtain after the shoes have been removed?  
  **Answer:** Bicycle.

- <span style="color:green;">**Bad Question:** What is the color of the curtain?  
  **Answer:** Green.  
  (*This question can be answered by the 3D scene visualization alone.*)</span>

<span style="color:brown;">**Scene Change:** A standing lamp has been added next to the couch near the backpack for more lighting.</span>

- **Good Question:** Which object is farther from the standing lamp, the coffee table or the bed?  
  **Answer:** Bed.

<span style="color:brown;">**Scene Change:** The refrigerator door is open, with food items visible inside.</span>

- **Good Question:** How many trash cans are near the opened refrigerator door after the change?  
  **Answer:** Two.

<img style='display: block; margin: auto; max-width: 30%; max-height: 30%;' src='data:image/png;base64,{}'/>

If you encounter any issues with the scene, please refresh the page to load a new one. Once you have finished the task, click the **Submit** button to receive your Completion Code.

*Please use your imagination and creativity to come up with unique and interesting movements!*
"""


@st.cache_resource
def render_img_html(image_b64):
    st.markdown(f"<img style='max-width: 40%;max-height: 40%;' src='data:image/png;base64, {image_b64}'/>", unsafe_allow_html=True)

@st.cache_resource
def image_to_base64(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    target_size = (700, 700)
    resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    
    _, encoded_image = cv2.imencode(".png", resized_image)
    base64_image = base64.b64encode(encoded_image.tobytes()).decode("utf-8")
    return base64_image

with st.expander("**Data Collection Guidelines --Please Read**", expanded=True, icon="📝"):
    image_path = "example.png"
    st.markdown(guideline_text.format(image_to_base64(image_path)), unsafe_allow_html=True)

left_col, right_col = st.columns([2, 1])


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
    
num_pairs = 4
with right_col:
    scene_id = st.session_state.scene_id
    change_description = st.session_state.change_description

    for i in range(1, num_pairs + 1):
        # Use placeholders to display the question and answer labels inside the text boxes
        st.markdown(f"<span style='color:red; font-weight:bold;'>Context Change:</span> {change_description[i-1]}", unsafe_allow_html=True)

        st.text_input(f"**Question {i}**", key=f"question{i}", placeholder="Type your question here...")

        st.text_input(f"**Answer {i}**", key=f"answer{i}", placeholder="Type your answer here...")

        # Add a small divider, reduce margin for a cleaner look
        st.markdown("<hr style='margin: 5px 0; height: 1px; border: none; background-color: #e0e0e0;'>", unsafe_allow_html=True)
    if st.button("Submit"):
        # Extract changes using list comprehension
        questions = [st.session_state.get(f'question{i}') for i in range(1, 5)]
        answers = [st.session_state.get(f'answer{i}') for i in range(1, 5)]
       
        # Check if all changes are unique and non-empty
        if len(set(questions)) < len(questions):
            st.warning("Please ensure that all changes are unique.")
        elif not all(questions):
            st.warning("Please fill in all the changes.")
        elif not all(len(q.split()) >= 8 for q in questions):  # Check if each change has at least 10 words
            st.warning("Please ensure that all questions are at least 8 words long.")
        else:
            # Proceed with success case
            st.session_state.survey_code = generate_survey_code()
            st.success(f"Congratulations! Your Completion Code is: {st.session_state.survey_code}. Please submit this code to CloudResearch.")
            
            # Prepare entry for saving
            entry = {
                'scene_id': scene_id,
                'changes': change_description,
                'questions': questions,
                'answers': answers,
                'survey_code': st.session_state.survey_code
            }
            save_context_data(entry)


