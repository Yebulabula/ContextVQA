import os
import copy
import time
import json
import streamlit as st
from datasets import load_dataset
from PIL import Image


DATA_DIR = "data/mp3d"
TASK_SPLITS = ['top_view_understanding', 'spatial_understanding', 'spatial_reasoning']
HUMAN_EVAL_DIR = "human_eval_results"


@st.cache_data
def obtain_all_scenes():
    scene_ids_list = [i for i in os.listdir(DATA_DIR) if not os.path.isfile(i)]
    return scene_ids_list


@st.cache_data
def load_data(scene_id, task_split, question_type):
    loaded_data = load_dataset(
        "utils/TVSR.py",
        # scene_id=scene_id,
        task_split=task_split,
        question_type=question_type,
        download_mode='force_redownload',
        ignore_verifications=True
    )['val']
    return loaded_data


@st.cache_data
def load_rgb_img(rgb_img_dir):
    return Image.open(rgb_img_dir)


@st.cache_data
def load_semantic_img(semantic_img_dir):
    return Image.open(semantic_img_dir)


def load_existed_annotation(file):
    if os.path.exists(file):
        with open(file) as e_annotation:
            annotation = json.load(e_annotation)
    else:
        raise FileExistsError
    return annotation


scene_list = obtain_all_scenes()

st.title('Data Explorer for Top-View Spatial Understanding and Reasoning')
with st.sidebar:
    user = st.selectbox(
        'Select a user',
        ["Chengzu", "Caiqi", "Han", "Ivan"]
    )
    scenario = st.selectbox(
        'Select a scene',
        scene_list
    )
    task = st.selectbox(
        'Select a task split',
        TASK_SPLITS
    )
    q_type = st.selectbox(
        'Select a question type',
        ['qa']
    )

st.subheader(f'Hi, {user}')

record_dir = os.path.join(HUMAN_EVAL_DIR, user.lower())

if not os.path.exists(record_dir):
    os.makedirs(record_dir)

store_file = f"{record_dir}/{scenario}-{task}-{q_type}.json"

data = load_data(scene_id=scenario, task_split=task, question_type=q_type)

data_num = len(data)
data_idx = st.number_input(
    f'Insert the index of the data item you want to see: range from 0 to {data_num-1}',
    min_value=0,
    max_value=data_num-1,
    value=0
)
if os.path.exists(store_file):
    annotated_data = load_existed_annotation(store_file)
    if data_idx in annotated_data['annotated_idx']:
        st.markdown("`Annotated! Please change another one! `")

data_item = data[data_idx]
rgb_img_file = data_item['rgb_map']
semantic_img_file = data_item['semantic_map']

col1, col2 = st.columns(2)

with col1:
    rgb_img = load_rgb_img(rgb_img_file)
    st.image(rgb_img, caption=f"RGB top-view map for scene {scenario}", width=350)

    st.subheader(data_item['question'])
    rgb_choices = st.multiselect(
        "Select one or more options that answer the question above correctly according to the top-view map above. ",
        data_item['choices'],
        key="rgb"
    )

with col2:
    semantic_img = load_semantic_img(semantic_img_file)
    st.image(semantic_img, caption=f"Semantic top-view map for scene {scenario}", width=350)

    st.subheader(data_item['question'])
    semantic_choices = st.multiselect(
        "Select one or more options that answer the question above correctly according to the top-view map above. ",
        data_item['choices'],
        key="semantic"
    )

st.subheader("Golden Labels")
with st.expander("Click to see the golden answer"):
    st.text(data_item['labels'])
    st.text("Hard to answer" if data_item['hard_to_answer'] else "")

whether_rgb_semantic_same = set(rgb_choices) == set(semantic_choices)
whether_rgb_correct = set(rgb_choices) == set(data_item['labels'])
whether_semantic_correct = set(semantic_choices) == set(data_item['labels'])

if st.button("Submit"):
    annotated_data_item = copy.deepcopy(data_item)
    annotated_data_item['rgb_semantic_consistency'] = whether_rgb_semantic_same
    annotated_data_item['rgb_correct'] = whether_rgb_correct
    annotated_data_item['semantic_correct'] = whether_semantic_correct
    annotated_data_item['rgb_choices'] = rgb_choices
    annotated_data_item['semantic_choices'] = semantic_choices
    annotated_data_item['submit_gmt_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

    if os.path.exists(store_file):
        with open(store_file, "r") as f:
            annotated_data = json.load(f)
            annotated_data["annotated_idx"].append(data_idx)
            annotated_data["annotation"].append(annotated_data_item)
    else:
        annotated_data = {
            "annotated_idx": [data_idx],
            "annotation": [annotated_data_item]
        }

    with open(store_file, "w") as f:
        json.dump(annotated_data, f, indent=4)

        st.success("Annotation submitted!")
        st.balloons()

if os.path.exists(store_file):
    with open(store_file, "r") as f:
        btn = st.download_button(
            label="Download annotations",
            data=f,
            file_name=os.path.basename(store_file),
            mime='text'
        )