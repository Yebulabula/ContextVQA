import streamlit as st
import plotly.graph_objects as go
import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import random



# firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

firebase_credentials = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY29udGV4dHZxYSIsCiAgInByaXZhdGVfa2V5X2lkIjogIjNiMWVhOGQ5ZjBjMDJiYjEwZDQwNTI4YWFlNWFmODI0MDAzMzZlZDEiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRQ1kvdkV3QkpkN2RUcW1cblZkeHFVcExFMFFldTRFbS96dVA3YlV5YmxzUUZrVzhoNjBUUGdORlp0UXo2Z012L1VpZFBIcGxaSjRHWDVLZFhcbldVd2wrZkpHM2phZFhPcEJsaFlXaTBiNGhkWEhOY3NWSjR1dlFab0xrM05IcUJCbGhzSTU5eS96VU9QTTExc2xcbkRIVXVTL3ZhaGg4VHBwWEVubnRGV2lxNkYrTitmQmxhL3BtQlA1RDNuNG5qMnhObzgwbWsva3V3UjY0akpSZC9cbkVXeTZUaGExOXhPc3hWUFhCRUxFRXlLTGY2RzYwbU9jbnZpQWRwcU5MU2J0MUlwZUMwaWw0RlFuQUcwUUR3c3FcbmE5ay90b2t0OWs2NUFzc085dFcvVjcrTzVodmlySXUwL1pneXV3bGowbmNGRHNYb211UTRndXQ0Q3g3UUp2bndcbnA5Q3BMNTJaQWdNQkFBRUNnZ0VBRUNIdHo3amtPajNwd2NsUzlSa2c1Y1QrME9kUWozdWkyWXUwWk1HWWlOZkZcbmhxZVd1V1NsYnBhak9EVGxqZFlkVS8vdmZwR21YaHhic3QrMUlsb0JQSXpJNkgzNEs1TkdYL2t1c2h6MnBrdGJcblR5ODgwTzJUYno0TWpWVkE2VnUwMWtUazF2ekVFSUR5Mk95LzNISmhxN0N4elRJbkg3VHdYYWM4MHlPYXR1YjRcblRWMGNFYXRnVUdHQlJudjRzbVVmVG1LeU9MeFkvdWxEbllPTWtmRXlEL2lzaVlhaTBCbEY4RC9CbGlCVmJEVERcbk0veEthM21yYkh0YU0zTVVLVVdWZ1JFTFlOU0IwbWcxRGVDdldSM2RwQ1JxSUg4dWJzMGlGc0JvVG4vb0NNbUpcbkdpaHA1OGtTSlV2d2c3YWJSKzRpd2liaktrdFhEYjRrejFiNlN2MElTd0tCZ1FESlBObE8vMk12ZmtwZ1h6SDhcbmlnNW1CbGI2VWRkR29QT1pBTDdmeHpDVTd1TmtTTHJXUEVkY2gzcDNKV05tNDR6SWp0czJqd0VaZHBWdXdxTS9cbnY1Q2lwZExHMCtEMUhIL1BJK2lhUUJLWWExbHZWMHI0S2kxVWJiVFYzOVBPbkJ1S2RIZ3BRNkRhUS9tQ2RTK2hcbnkwQllXd0NJdUIzRUg1Wk5pTDY4azJHMnV3S0JnUURDb1ZnVkUvTTgrWnVpZUlUanZDSk5hNUYrakVMaXlQVlVcbitXRlBXQkpmN2tmRktuZHRleXdiZUR0U2NJRWV5OXJyVWo0anRyMCs2NDM0UTVoS2pPM2Q3c1VGRTlxcms2K09cbngrOUhtYlB6OGg3N3d2TXc3dXFncFEvZzlwUkJOZGFHS2FCMGszUWh6OFY2QXQra01sZkN6NXl0RGk5SUZ3c0RcblM3VmdqQ2E1dXdLQmdBemMyOU1GMWZRcU1WelptTnRZZzdVWHdLVjlaN0kzQlhzSkppb3RsRGhnMEo0UFhBbm5cbmpuUW1vTGhPNW55a0hOS1E5d2dVdWZCRHVTZDhQMjBLdEpjQTNHa2pEK1Q2N2x4eUlpTUI1MjVncGpYTXNaa05cbk1ScU5iSnFqRk9uRzVxZkI3QkJQSjAvc09sMlJXZnNRZjh0bC9iRy9lditYT1VjNWIxK2tXQUdUQW9HQURyTk5cbkNkcUY1cmNic0R2V0hiVmFDZXIwQkZEbnhHVlZVbU83bTlpVkdyWE9xZSs1TVlXNklTRUZxZ1poV2tnZmN1SzFcbld0RTBuZ29Bb1IzSjVPZWNGOFV2RUdFZGhSUVVrSDQ5Ym5VSGlJZGpHN1R2MVdSV1NHZnZPUmltdmY0cEE5MGxcbkIya1R2bklKQWx3eE5CK3hUVCtOSCswUVdTdVVZMTFXaDhKT01uMENnWUVBaHlYUGkxaC9MMWZybW1lWFlKTWRcblpROEhrT3dTVGdrelF6eER4WWttQ1dJN1lIeThzbU9SUGRSRlBOVEpUMVVRU0Y1d2Mwd1pENlUvTnFKMGlqTEtcblFqYzBOVUlkNmhlVFQ3cXpwdnp4VFZCcFNtbFJCVm1MTGJ3Q0plditQajczaU0rZEtSemIxYmpBQ1lEamM5OWhcbjhVazFDZW1GWXhzS2s5Z1Y0bktaQ2M4PVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLXRxc2I3QGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA1OTg2MTIxMjI3NjY5MjQ1MDM1IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay10cXNiNyU0MGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"


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

@st.cache_data
def get_scene_ids_and_files(root_dir):
    scene_ids = sorted(os.listdir(root_dir), key=lambda x: (not x.startswith('scene'), x))
    return {scene_id: os.path.join(root_dir, scene_id, f'{scene_id}_vh_clean_2.npz') for scene_id in scene_ids}

SCENE_ID_TO_FILE = get_scene_ids_and_files(ROOT_1)

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
        width=1000,
        height=800,
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

initialize_state()

guideline_text = """

**<span style="color:blue;">Randomly select a scene ID, preferably avoiding the default option.</span>**

**Step 1:** Rotate the given 3D visualization and read scene descriptions to understand the 3D scene.

**Step 2:** In the form, write descriptions of context changes, craft related questions, and provide concise answers.

**Step 3:** Submit your responses.

###### Context Change - Imagine a potential change that could take place in the 3D scene.
- Changes can be:
- **Object Geometric Change** (e.g., object movement, rotation, shape transformation): *The backpack has been moved from the desk to the black chair.*
- **Object Attribute Change** (e.g., color, texture, functionality, state): *The toilet paper hanging on the wall has been completely used.*
- **Object Addition/Removal** (e.g., adding or removing objects): *The orange couch in the room is removed.*
- **Local context change** (one object changes); **Global context change** (multiple objects change).
- Ensure the changes are feasible within the 3D scene layout, **realistic**, **precise**, and **detailed**. Otherwise they will be <span style="color:red;">rejected</span>.
- <span style="color:red;"> **Good example:** </span> The laundry basket that was on the bed has been moved the left of the round wooden table.
- <span style="color:green;"> **Bad example:** </span> The laundry basket has been moved to table.

- <span style="color:red;"> **Good example:** </span> Two red coffee tables has been added between the only two armchairs in the room.
- <span style="color:green;"> **Bad example:** </span> Several tables have been added to the room.

- <span style="color:red;"> **Good example:** </span> The yellow desk in the corner is now being used as the dining table for the guests..
- <span style="color:green;"> **Bad example:** </span> The yellow desk is now being used as a television.

###### Question - Ask a question about the 'modified' scene.
- The questions that yield the same answer in both 'original' scene and 'changed' scene will be <span style="color:red;">rejected</span>.
- The questions that have **multiple**, **ambiguous**, or **subjective** answers will be <span style="color:red;">rejected</span>.
- The questions that can be answered by merely reading context change will be <span style="color:red;">rejected</span>.

- <span style="color:red;"> **Good example:** </span> **Context Change**: The black armchair next to the couch becomes red. **Q**: Does the black armchair now match the color scheme of other furnitures around the couch?
- <span style="color:green;"> **Bad example:** </span> **Context Change**: The black armchair next to the couch becomes red. **Q**: What color is the armchair next to the couch?

- <span style="color:red;"> **Good example:** </span> **Context Change**: Three more trash cans are added near the kitchen counter. **Q**: How many trash cans are there in total in this room now?
- <span style="color:green;"> **Bad example:** </span> **Context Change**: Three more trash cans are added near the kitchen counter. **Q**: Is there a kicthen counter in the room?

- <span style="color:red;"> **Good example:** </span> **Q**: Is the white cabinet, relative to the fridge, closer to the piano now?
- <span style="color:green;"> **Bad example:** </span> **Q**: Is the white cabinet close to the piano?

###### Answer - Provide a simple word or phrase as an answer to the question.
- The answer should be directly related to the question and make sense in the context of the modified scene.
- <span style="color:red;"> **Good example:** </span> **Context Change**: The bed has a lot of stuff on it, so it is cannot be used now. **Q**: Where is another good place to sit and rest? **A**: Couch.
- <span style="color:green;"> **Bad example:** </span> **Context Change**: The bed has a lot of stuff on it, so it is cannot be used now. **Q**: Where is another good place to sit and rest? **A**: If you want to rest, I suggest you sit on the couch for a while.


**Note:** Each context change can be used for multiple questions. Ensure all context changes, questions, and answers are diverse and unique. If you're stuck, try selecting a new scene—we have a total of 800 scenes available for you to choose from. 


*<span style="color:red;">Please use your imagination to its fullest. Good luck!</span>* 😁
"""

# Display the guideline at the beginning of the form
with st.expander("**Data Collection Guidelines --Please Read**", expanded=True, icon="📝"):
    st.markdown(guideline_text, unsafe_allow_html=True)
    
                
left_col, right_col = st.columns([2, 1])


# Right column: Form
with right_col:
    scene_id = st.selectbox("Select a Scene ID", list(SCENE_ID_TO_FILE.keys()))

    smaller_bold_context = "<div style='font-weight: bold; font-size: 20px;'>Context Change</div>"
    smaller_bold_question = "<div style='font-weight: bold; font-size: 20px;'>Question</div>"
    smaller_bold_answer = "<div style='font-weight: bold; font-size: 20px;'>Answer</div>"

    tags_1 = ["Object Geometric Change", "Object Attribute Change", "Object Addition or Removal"]
    tags_2 = ["Local Change", "Global Change"]
    
    selected_tags_1 = st.selectbox("Select Type of Change", options=tags_1, key="selected_tags_1")
    selected_tags_2 = st.selectbox("Select Scale of Change", options=tags_2, key="selected_tags_2")

    st.markdown(smaller_bold_context, unsafe_allow_html=True)
    context_change = st.text_area("Describe any changes that could reasonably occur in the scene.", key="context_change", placeholder="Type here...", height=10)
    
    if st.button("Need Inspiration for Context Change?"):
        st.info(random.choice(context_inspirations))
    
    st.markdown(smaller_bold_question, unsafe_allow_html=True)
    question = st.text_area("Write a question related to the context change.", key="question", placeholder="Type here...", height=10)

    if st.button("Need Inspiration for Question?"):
        st.info(random.choice(question_inspirations))
    
    st.markdown(smaller_bold_answer, unsafe_allow_html=True)
    answer = st.text_area("Provide a concise answer.", key="answer", placeholder="Type here...", height=10)

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
    <div style='margin-top: 10px;'>
        <p>You've submitted <span style='color: red; font-weight: bold;'>{st.session_state.responses_submitted}</span> responses. </span></p>
    </div>
    """
    st.markdown(final_section_html, unsafe_allow_html=True)
    
with left_col:
    ply_file = SCENE_ID_TO_FILE[scene_id]
    mesh_data = load_mesh(ply_file)
    vertices, triangles, vertex_colors = mesh_data.values()
    vertex_colors = vertex_colors[:, :3]

    instance_labels, id2labels = read_instance_labels(scene_id)
    id2labels = {int(k): v for k, v in id2labels.items()}

    annotations = scene_annotations[scene_id]
    
    initialize_plot(vertices, triangles, vertex_colors, annotations, id2labels)
    
    
    
