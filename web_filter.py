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
SCENE_IDs = sorted([scene for scene in os.listdir(ROOT_1)])

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

First, explore the 3D scene and think about how you could modify **one or more objects** within it. Then, describe **five distinct changes**. Follow these important rules:

1. **Natural, Contextual Changes**: Any change that fits seamlessly within the scene's layout and context is acceptable. For example, you might:
   - Rearrange objects (e.g., move a chair to a different location).
   - Modify the visual appearance of objects (e.g., change the color of a lamp).
   - Adjust the functionality or state of objects (e.g., open or close a door).
   - Add, remove, or replace objects in the scene.
   - ...and much more!

2. **Detailed, Deterministic Descriptions**: Be precise and specific. Use nearby objects or unique attributes to clearly identify the objects you're changing. Make sure to describe exactly *how* the change occurs. Avoid vague or uncertain language like "maybe," "could be," or "either...or." Each description is at least 10 words long.

   <span style="color:red;">**Bad examples:**</span>
   - The black chair is removed. (Too brief.)
   - The table could be longer. (Vague—what table? How much longer?)
   - Door has opened. (Unclear—which door?)
   - The cup could either be removed or placed on the table. (Indecisive—removed or placed?)

   <span style="color:green;">**Good example:**</span>
   - A coffee machine has been added to the kitchen counter next to the toaster oven for added convenience.

3. **Unique and Varied Changes**: Each of your five changes must be unique and applied to different objects. **Repetitive changes** will be <span style="color:red;">rejected</span>, but creative and diverse changes may receive a <span style="color:green;">bonus</span>.

**Note**: Overall, to ensure data quality, we encourage you to make thoughtful, detailed changes. Avoid overly simple or repetitive modifications. If your scene seems too simple, feel free to refresh the page for a new one. However, all changes must be based on the same scene. After submitting your changes, you’ll receive a completion code—be sure to save this and submit it to CloudResearch to claim your payment.

<span style="color:red;">**Unleash your creativity! Good luck!**</span> 😁
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
        elif not all(len(change.split()) >= 10 for change in changes):  # Check if each change has at least 10 words
            st.warning("Please ensure that all changes are at least 10 words long.")
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
