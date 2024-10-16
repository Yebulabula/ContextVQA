import json
import os
import base64
import concurrent.futures
import re
from openai import OpenAI

ROOT_DIR = "/mnt/new_drive/Documents/ContextVQA/3D_scans"
client = OpenAI(api_key="")


# Load the movement changes once and reuse
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_changes_to_list(text):
    """Extract the first sentence from each change."""
    return [change.split('.')[1].strip() for change in text.strip().split("\n\n")]

def load_json(file_path):
    """Loads JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def read_instance_labels(scene_id):
    """Reads instance labels for a given scene."""
    return load_json(f'{ROOT_DIR}/{scene_id}/{scene_id}_id2labels.json')

def encode_image(image_path):
    """Encodes an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def append_request_to_jsonl(request, file_path='requests.jsonl'):
    """Appends request as a new line to a .jsonl file."""

    with open(file_path, 'a') as f:
        json.dump(request, f)
        f.write('\n')

def collect_requests(preprocess_data, system_content, prompt, split_ratio):
    """Collects requests by reading and processing files in the directory."""
    
    for i, (k,v) in enumerate(preprocess_data.items()):
        context_changes = list(v.keys())
        
        
        for j, change in enumerate(context_changes):
            questions = v[change]
            
            questions = '\n'.join(questions)
            text = prompt.format(change = change, questions=questions)
            request = {
                "custom_id": f"{k}_{j}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": text}
                    ]
                }
            }
        
            request_filename = f'requests/requests_{i}.jsonl'
            append_request_to_jsonl(request, file_path=request_filename)

def show_status(num):
    batch = client.batches.list(limit=num).data
    for i, d in enumerate(batch):
        print(f'Batch ID: {d.id}, ', f'Status: {d.status}', f'Ouput File ID: {d.output_file_id}', f'Input File ID: {d.input_file_id}')

def upload_tasks(request_files):
    for request in request_files:
        batch_input_file = client.files.create(
          file=open(f"requests/{request}", "rb"),
          purpose="batch"
        )

        batch_input_file_id = batch_input_file.id

        client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
              "description": "nightly eval job"
            }
        )
        
prompt_template = '''
### Task Description
We have a context change and a corresponding list of questions.

The context change refers to a modification made to the original scene. The questions are focused on the state of the scene after this change has occurred.

Your task is to simplify the list of questions, making them more concise and easier to understand. However, ensure that each question clearly emphasizes that it is referring to the scene after the context change.

### Context Change
{change}

### Questions
{questions}

The format of your response should be in JSON format as follows:
{{
    "text of context change": [
        "concised question 1",
        "concised question 2",
        "concised question 3",
        ...
    ]
}}
'''

def split_text(json_string, scene_id):
    # Use regex to find the JSON portion (anything within curly braces)
    json_data = re.search(r'{.*}', json_string, re.DOTALL)
    
    json_clean_string = json_data.group(0)
    data = json.loads(json_clean_string)
    
    # Update dictionary structure with scene_id
    # data_with_scene_id = {f"{scene_id}": data}
    
    return data
    
def fetch_file_content(file_id):
    """Fetches file content from OpenAI."""
    try:
        return client.files.content(file_id).read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching file {file_id}: {e}")
        return None

def count_changes(scenes):
    total_changes = 0
    
    # Iterate through each scene in the dictionary
    for scene_id, changes in scenes.items():
        # For each change category in the scene
        for category, descriptions in changes.items():
            # Add the number of descriptions in the category to the total count
            total_changes += len(descriptions)
    
    return total_changes

def extract_data(total_number_of_files):
    """Extracts data from batches and processes them in parallel."""
    batch = client.batches.list(limit=total_number_of_files).data
    
    data = []

    file_ids = [(d.input_file_id, d.output_file_id) for d in batch if d.status == 'completed']

    # Fetch files in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        input_file_contents = list(executor.map(fetch_file_content, [pair[0] for pair in file_ids]))
        output_file_contents = list(executor.map(fetch_file_content, [pair[1] for pair in file_ids]))

    # Process fetched data
    for input_content, output_content in zip(input_file_contents, output_file_contents):
        if input_content and output_content:
            # Extract custom_id and context change from the input content
            ids = []
            context_changes = {}
            
            # Process input content to extract custom_id and context change
            for line in input_content.splitlines():
                try:
                    input_data = json.loads(line)
                    custom_id = input_data.get("custom_id")
                    if custom_id:
                        ids.append(custom_id)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in input: {e}")
            
            # Process output content and match it with corresponding custom_id and context change
            for count, line in enumerate(output_content.splitlines()):
                try:
                    output_data = json.loads(line)
                    completion_content = output_data["response"]["body"]["choices"][0]["message"]["content"]
                    if count < len(ids):
                        custom_id = ids[count]
                        data.append({
                            "custom_id": custom_id,
                            "completion_content": completion_content,
                        })
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in output: {e}")

    # Build scene descriptions
    scene_descriptions = {}

    for entry in data:
        # Extract scene_id and description from the entry
        scene_id = "_".join(entry['custom_id'].split('_')[0:2])
        description = entry['completion_content']
        
        # Split the description into questions
        questions = split_text(description, scene_id)

        # Initialize the scene_id dictionary if it doesn't exist
        scene_descriptions.update(questions)
                

    with open('GPT_responses.json', 'w', encoding='utf-8') as outfile:
        json.dump(scene_descriptions, outfile, indent=4, ensure_ascii=False)
        
ROOT_1 = '/mnt/new_drive/Documents/ContextVQA/3D_scans'
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def read_instance_labels(scene_id):
    return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

if __name__ == '__main__':
    from openai import OpenAI
    import random
    
    data = load_json('filtered_v4.json')

    system_content = "You are an AI language assistant tasked to help make the texts concise."

    collect_requests(data, system_content, prompt_template, 5)
        
    # requqest_files = os.listdir('requests')[100:]
    # upload_tasks(requqest_files)
    # show_status(9)
    
    # extract_data(9)