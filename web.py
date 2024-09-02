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

# Initialize Firebase credentials (dummy credentials for example)
# firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

firebase_credentials="ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY29udGV4dHZxYSIsCiAgInByaXZhdGVfa2V5X2lkIjogIjNiMWVhOGQ5ZjBjMDJiYjEwZDQwNTI4YWFlNWFmODI0MDAzMzZlZDEiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRQ1kvdkV3QkpkN2RUcW1cblZkeHFVcExFMFFldTRFbS96dVA3YlV5YmxzUUZrVzhoNjBUUGdORlp0UXo2Z012L1VpZFBIcGxaSjRHWDVLZFhcbldVd2wrZkpHM2phZFhPcEJsaFlXaTBiNGhkWEhOY3NWSjR1dlFab0xrM05IcUJCbGhzSTU5eS96VU9QTTExc2xcbkRIVXVTL3ZhaGg4VHBwWEVubnRGV2lxNkYrTitmQmxhL3BtQlA1RDNuNG5qMnhObzgwbWsva3V3UjY0akpSZC9cbkVXeTZUaGExOXhPc3hWUFhCRUxFRXlLTGY2RzYwbU9jbnZpQWRwcU5MU2J0MUlwZUMwaWw0RlFuQUcwUUR3c3FcbmE5ay90b2t0OWs2NUFzc085dFcvVjcrTzVodmlySXUwL1pneXV3bGowbmNGRHNYb211UTRndXQ0Q3g3UUp2bndcbnA5Q3BMNTJaQWdNQkFBRUNnZ0VBRUNIdHo3amtPajNwd2NsUzlSa2c1Y1QrME9kUWozdWkyWXUwWk1HWWlOZkZcbmhxZVd1V1NsYnBhak9EVGxqZFlkVS8vdmZwR21YaHhic3QrMUlsb0JQSXpJNkgzNEs1TkdYL2t1c2h6MnBrdGJcblR5ODgwTzJUYno0TWpWVkE2VnUwMWtUazF2ekVFSUR5Mk95LzNISmhxN0N4elRJbkg3VHdYYWM4MHlPYXR1YjRcblRWMGNFYXRnVUdHQlJudjRzbVVmVG1LeU9MeFkvdWxEbllPTWtmRXlEL2lzaVlhaTBCbEY4RC9CbGlCVmJEVERcbk0veEthM21yYkh0YU0zTVVLVVdWZ1JFTFlOU0IwbWcxRGVDdldSM2RwQ1JxSUg4dWJzMGlGc0JvVG4vb0NNbUpcbkdpaHA1OGtTSlV2d2c3YWJSKzRpd2liaktrdFhEYjRrejFiNlN2MElTd0tCZ1FESlBObE8vMk12ZmtwZ1h6SDhcbmlnNW1CbGI2VWRkR29QT1pBTDdmeHpDVTd1TmtTTHJXUEVkY2gzcDNKV05tNDR6SWp0czJqd0VaZHBWdXdxTS9cbnY1Q2lwZExHMCtEMUhIL1BJK2lhUUJLWWExbHZWMHI0S2kxVWJiVFYzOVBPbkJ1S2RIZ3BRNkRhUS9tQ2RTK2hcbnkwQllXd0NJdUIzRUg1Wk5pTDY4azJHMnV3S0JnUURDb1ZnVkUvTTgrWnVpZUlUanZDSk5hNUYrakVMaXlQVlVcbitXRlBXQkpmN2tmRktuZHRleXdiZUR0U2NJRWV5OXJyVWo0anRyMCs2NDM0UTVoS2pPM2Q3c1VGRTlxcms2K09cbngrOUhtYlB6OGg3N3d2TXc3dXFncFEvZzlwUkJOZGFHS2FCMGszUWh6OFY2QXQra01sZkN6NXl0RGk5SUZ3c0RcblM3VmdqQ2E1dXdLQmdBemMyOU1GMWZRcU1WelptTnRZZzdVWHdLVjlaN0kzQlhzSkppb3RsRGhnMEo0UFhBbm5cbmpuUW1vTGhPNW55a0hOS1E5d2dVdWZCRHVTZDhQMjBLdEpjQTNHa2pEK1Q2N2x4eUlpTUI1MjVncGpYTXNaa05cbk1ScU5iSnFqRk9uRzVxZkI3QkJQSjAvc09sMlJXZnNRZjh0bC9iRy9lditYT1VjNWIxK2tXQUdUQW9HQURyTk5cbkNkcUY1cmNic0R2V0hiVmFDZXIwQkZEbnhHVlZVbU83bTlpVkdyWE9xZSs1TVlXNklTRUZxZ1poV2tnZmN1SzFcbld0RTBuZ29Bb1IzSjVPZWNGOFV2RUdFZGhSUVVrSDQ5Ym5VSGlJZGpHN1R2MVdSV1NHZnZPUmltdmY0cEE5MGxcbkIya1R2bklKQWx3eE5CK3hUVCtOSCswUVdTdVVZMTFXaDhKT01uMENnWUVBaHlYUGkxaC9MMWZybW1lWFlKTWRcblpROEhrT3dTVGdrelF6eER4WWttQ1dJN1lIeThzbU9SUGRSRlBOVEpUMVVRU0Y1d2Mwd1pENlUvTnFKMGlqTEtcblFqYzBOVUlkNmhlVFQ3cXpwdnp4VFZCcFNtbFJCVm1MTGJ3Q0plditQajczaU0rZEtSemIxYmpBQ1lEamM5OWhcbjhVazFDZW1GWXhzS2s5Z1Y0bktaQ2M4PVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLXRxc2I3QGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA1OTg2MTIxMjI3NjY5MjQ1MDM1IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay10cXNiNyU0MGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"

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
    db.collection('ContextVQA').add(data)

# Streamlit app configuration
st.set_page_config(
    page_title="ContextQA Data Collection App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ContextQA")

ROOT_1 = "3D_scans"
SCENE_IDs = sorted([scene for scene in os.listdir(ROOT_1) if scene.startswith('scene')])
SCENE_ID_TO_FILE = {scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in SCENE_IDs}

context_inspirations = load_json('context_inspirations.json')
question_inspirations = load_json('question_inspirations.json')
scene_annotations = load_scene_annotations()

def read_instance_labels(scene_id):
    return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

def generate_survey_code():
    return 'CQA_' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))

@st.cache_resource
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

def initialize_plot(vertices, triangles, vertex_colors, annotations):
    vertex_colors_rgb = [f'rgb({r}, {g}, {b})' for r, g, b in vertex_colors]

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

initialize_state()

def refresh_scene():
    st.session_state.scene_id = random.choice(list(SCENE_ID_TO_FILE.keys()))
    scene_id = st.session_state.scene_id
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    
    annotations = scene_annotations[scene_id]
    return initialize_plot(vertices, triangles, vertex_colors, annotations)

guideline_text = """
<span style="color:brown;">**Welcome!**</span> 

You need to firstly understand the given 3D scene. Then, think of a hypothetical change the scene you can make to the scene and write it down. After that, imagine what the scene looks like with the change and ask a question about the 'changed' scene. Finally, give a concise answer to your question. <span style="color:red;">**Repeat this process for three times to complete the task.**</span>

###### Scene Change
- Imagine a change that could happen in the scene. This is just pretend, so you don't need to actually change anything in the scene. You can think of moving, rotating, resizing, or changing the color, state, adding, or removing objects—any **realistic change** is fine.
- To avoid <span style="color:red;">**rejection**</span>, your description of the change must be clear enough so we know exactly which object(s) you changed. 

###### Question - Ask a question about the scene following the scene change.
- Your questions **shouldn't** be answered solely by reading the Scene Change without viewing the scene.
- Your questions **shouldn't** give the same answer, no matter whether the scene change happened.
- Your questions **shouldn't** have **multiple**, **ambiguous**, **subjective**, or **yes/no** answers to avoid <span style="color:red;">**rejection**</span>.

###### Answer - Your answer has to be a simple word or a phrase, and <span style="color:red;"> **unique** </span> to the question.

**Example:**

<img style='display: block; margin: auto; max-width: 30%; max-height: 30%;' src='data:image/png;base64,{}'/>

- <span style="color:red;"> **Good:** </span> **Scene Change:** The gray coffee table has been removed from the room. **Q:** Which piece of furniture is directly behind the shelf now? **Answer:** Couch.
- <span style="color:red;"> **Good:** </span> **Scene Change:** The brown pillow that was on the bed has been moved to the gray couch. **Q:**  What is the closest item in front of the pillow now? **Answer:** Coffee table.
- <span style="color:green;">**Bad:**</span> **Scene Change:** The brown pillow that was on the bed has been moved to the gray couch. **Q:** What color is the pillow? **A:** Brown. (**The pillow color is not affected by the change**)
- <span style="color:green;">**Bad:**</span> **Scene Change:** The brown pillow that was on the bed has been moved to the gray couch. **Q:** What is on the gray couch now? **A:** Pillow. (**The question can be answered by only reading the scene change**) 

<span style="color:blue;">**Note:** We do have some templates to inspire you. But these templates are not related to the scene you are looking at. You should not copy them. </span>

*<span style="color:red;"> If you're stuck, try to get a new scene. Be creative! Good luck!</span>* 😁
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
    image_path = "scene0000_00.png"
    st.markdown(guideline_text.format(image_to_base64(image_path)), unsafe_allow_html=True)

left_col, right_col = st.columns([2, 1])

with right_col:
    if 'scene_id' not in st.session_state:
        st.session_state.fig = refresh_scene()
        
    if st.button("**Click here for a new scene**"):
        st.session_state.fig = refresh_scene()
        
    scene_id = st.session_state.scene_id

    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Scene Change</div>", unsafe_allow_html=True)
    context_change = st.text_area("Imagine a change that is reasonably happen in the given 3D scene.", key="context_change", placeholder="Type here...", height=10)
    
    if st.button("Click here to view some example context changes."):
        st.info(random.choice(context_inspirations))
        
    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Question</div>", unsafe_allow_html=True)
    question = st.text_area("Imagine the scene after change, then ask a question.", key="question", placeholder="Type here...", height=10)
    
    if st.button("Click here to view some example questions."):
        st.info(random.choice(question_inspirations))

    st.markdown("<div style='font-weight: bold; font-size: 20px;'>Answer</div>", unsafe_allow_html=True)
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

            duplicates_query = db.collection('ContextVQA').where('scene_id', '==', scene_id) \
                                                .where('context_change', '==', context_change) \
                                                .where('question', '==', question) \
                                                .where('answer', '==', answer) \
                                                .stream()
            duplicates = list(duplicates_query)

            if duplicates:
                st.warning("This submission has already been made. Please do not submit duplicate entries.")
            else:
                survey_code = generate_survey_code()
                entry['survey_code'] = survey_code
                save_context_data(entry)
                
                st.success(f"Thanks for subitting your responses. Here is your Completion Code: {survey_code}. You need obtain 3 codes to complete the task.")

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
