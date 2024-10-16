
import plotly.graph_objects as go
import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import random

firebase_credentials="ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY29udGV4dHZxYSIsCiAgInByaXZhdGVfa2V5X2lkIjogIjNiMWVhOGQ5ZjBjMDJiYjEwZDQwNTI4YWFlNWFmODI0MDAzMzZlZDEiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRQ1kvdkV3QkpkN2RUcW1cblZkeHFVcExFMFFldTRFbS96dVA3YlV5YmxzUUZrVzhoNjBUUGdORlp0UXo2Z012L1VpZFBIcGxaSjRHWDVLZFhcbldVd2wrZkpHM2phZFhPcEJsaFlXaTBiNGhkWEhOY3NWSjR1dlFab0xrM05IcUJCbGhzSTU5eS96VU9QTTExc2xcbkRIVXVTL3ZhaGg4VHBwWEVubnRGV2lxNkYrTitmQmxhL3BtQlA1RDNuNG5qMnhObzgwbWsva3V3UjY0akpSZC9cbkVXeTZUaGExOXhPc3hWUFhCRUxFRXlLTGY2RzYwbU9jbnZpQWRwcU5MU2J0MUlwZUMwaWw0RlFuQUcwUUR3c3FcbmE5ay90b2t0OWs2NUFzc085dFcvVjcrTzVodmlySXUwL1pneXV3bGowbmNGRHNYb211UTRndXQ0Q3g3UUp2bndcbnA5Q3BMNTJaQWdNQkFBRUNnZ0VBRUNIdHo3amtPajNwd2NsUzlSa2c1Y1QrME9kUWozdWkyWXUwWk1HWWlOZkZcbmhxZVd1V1NsYnBhak9EVGxqZFlkVS8vdmZwR21YaHhic3QrMUlsb0JQSXpJNkgzNEs1TkdYL2t1c2h6MnBrdGJcblR5ODgwTzJUYno0TWpWVkE2VnUwMWtUazF2ekVFSUR5Mk95LzNISmhxN0N4elRJbkg3VHdYYWM4MHlPYXR1YjRcblRWMGNFYXRnVUdHQlJudjRzbVVmVG1LeU9MeFkvdWxEbllPTWtmRXlEL2lzaVlhaTBCbEY4RC9CbGlCVmJEVERcbk0veEthM21yYkh0YU0zTVVLVVdWZ1JFTFlOU0IwbWcxRGVDdldSM2RwQ1JxSUg4dWJzMGlGc0JvVG4vb0NNbUpcbkdpaHA1OGtTSlV2d2c3YWJSKzRpd2liaktrdFhEYjRrejFiNlN2MElTd0tCZ1FESlBObE8vMk12ZmtwZ1h6SDhcbmlnNW1CbGI2VWRkR29QT1pBTDdmeHpDVTd1TmtTTHJXUEVkY2gzcDNKV05tNDR6SWp0czJqd0VaZHBWdXdxTS9cbnY1Q2lwZExHMCtEMUhIL1BJK2lhUUJLWWExbHZWMHI0S2kxVWJiVFYzOVBPbkJ1S2RIZ3BRNkRhUS9tQ2RTK2hcbnkwQllXd0NJdUIzRUg1Wk5pTDY4azJHMnV3S0JnUURDb1ZnVkUvTTgrWnVpZUlUanZDSk5hNUYrakVMaXlQVlVcbitXRlBXQkpmN2tmRktuZHRleXdiZUR0U2NJRWV5OXJyVWo0anRyMCs2NDM0UTVoS2pPM2Q3c1VGRTlxcms2K09cbngrOUhtYlB6OGg3N3d2TXc3dXFncFEvZzlwUkJOZGFHS2FCMGszUWh6OFY2QXQra01sZkN6NXl0RGk5SUZ3c0RcblM3VmdqQ2E1dXdLQmdBemMyOU1GMWZRcU1WelptTnRZZzdVWHdLVjlaN0kzQlhzSkppb3RsRGhnMEo0UFhBbm5cbmpuUW1vTGhPNW55a0hOS1E5d2dVdWZCRHVTZDhQMjBLdEpjQTNHa2pEK1Q2N2x4eUlpTUI1MjVncGpYTXNaa05cbk1ScU5iSnFqRk9uRzVxZkI3QkJQSjAvc09sMlJXZnNRZjh0bC9iRy9lditYT1VjNWIxK2tXQUdUQW9HQURyTk5cbkNkcUY1cmNic0R2V0hiVmFDZXIwQkZEbnhHVlZVbU83bTlpVkdyWE9xZSs1TVlXNklTRUZxZ1poV2tnZmN1SzFcbld0RTBuZ29Bb1IzSjVPZWNGOFV2RUdFZGhSUVVrSDQ5Ym5VSGlJZGpHN1R2MVdSV1NHZnZPUmltdmY0cEE5MGxcbkIya1R2bklKQWx3eE5CK3hUVCtOSCswUVdTdVVZMTFXaDhKT01uMENnWUVBaHlYUGkxaC9MMWZybW1lWFlKTWRcblpROEhrT3dTVGdrelF6eER4WWttQ1dJN1lIeThzbU9SUGRSRlBOVEpUMVVRU0Y1d2Mwd1pENlUvTnFKMGlqTEtcblFqYzBOVUlkNmhlVFQ3cXpwdnp4VFZCcFNtbFJCVm1MTGJ3Q0plditQajczaU0rZEtSemIxYmpBQ1lEamM5OWhcbjhVazFDZW1GWXhzS2s5Z1Y0bktaQ2M4PVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLXRxc2I3QGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA1OTg2MTIxMjI3NjY5MjQ1MDM1IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay10cXNiNyU0MGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"

if firebase_credentials:
    # Decode the base64 encoded credentials
    cred_json = base64.b64decode(firebase_credentials).decode('utf-8')
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)

    # Initialize Firebase app if not already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    # Set up Firestore client
    db = firestore.client()

    def export_firestore_collection_to_json(collection_name, output_file):
        # Reference to the Firestore collection
        collection_ref = db.collection(collection_name)
        
        # Get all documents in the collection
        docs = collection_ref.stream()

        # Prepare a dictionary to hold the exported data
        data = {}

        # Iterate over documents and collect data
        for doc in docs:
            dict_data = {k:v for k, v in doc.to_dict().items() if k != 'survey_code'}
            
            # change the order of the keys
            dict_data = {'scene_id': doc.to_dict()['scene_id'], 'context_change': doc.to_dict()['change_description'], 'question': list(doc.to_dict()['questions_and_answers'].keys()), 'answer': list(doc.to_dict()['questions_and_answers'].values())}

            if doc.to_dict()['survey_code'] not in data:
                data[doc.to_dict()['survey_code']] = [dict_data]
            else:          
                data[doc.to_dict()['survey_code']].append(dict_data)
        
        # Write data to a JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False,indent=2)

    # Example: Export data from 'your-collection-name' to 'output.json'
    collection_name = 'New Answer'
    output_file = 'ContextQA_data.json'

    export_firestore_collection_to_json(collection_name, output_file)
    
    # count the number of questions
    data = json.load(open('ContextQA_data.json', 'r'))
    questions = []
    context_changes = []
    scenes = []
    
    bad_data = []
    for survey_code in data:
        if len(data[survey_code]) < 4:
            bad_data.append(survey_code)
        
        for item in data[survey_code]:
            questions.extend(item['question'])
            context_changes.append(item['context_change'])
            scenes.append(item['scene_id'])
    
    print(f'Number of bad data: {len(bad_data)}')
    print(f'Number of good data: {len(data) - len(bad_data)}')
    print(f'There are {len(set(context_changes))} context changes and {len(set(questions))} questions in the collection of {len(set(scenes))}')  # Number of questions
    

import pandas as pd

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
        
data = load_json('questions/filtered_v4.json')
 
for scene in data:
    if len(data[scene]) < 4:
        print(scene)   
    else:
        print(f'The number of context changes in {scene} is {len(data[scene])}')

# data_1 = load_json('questions/filtered_v5.json')

# unfinished_data = {}
# for scene in data_1:
#     unfinished_data[scene] = {}
#     for change in data_1[scene]:
#         if change not in context_changes:
#             for question in data_1[scene][change]:
#                 if question not in questions:
#                     if change not in unfinished_data[scene]:
#                         unfinished_data[scene][change] = [question]
#                     else:
#                         unfinished_data[scene][change].append(question)
                    
# save_json(unfinished_data, 'questions/filtered_v5.json')

# data = load_json('questions/filtered_v5.json')
# questions = []
# context_changes = []
# scenes = []
# for scene in data:
#     for change in data[scene]:
#         questions.extend(data[scene][change])
#         context_changes.append(change)
#         scenes.append(scene)
# print(f'There are {len(set(context_changes))} context changes and {len(set(questions))} questions in the new collection of {len(set(scenes))}')  # Number of questions

# participants = os.listdir('crowd')

# Total_Data = pd.DataFrame()
# for p in participants:
#     # read csv
#     data = pd.read_csv(f'crowd/{p}')
#     # get 'CompleteionCode' and CompletionTime columns

#     for i in range(data.shape[0]):
#         completion_code = str(data['CompletionCode'][i])
        
#         completion_time = str(data['Education'][i])
#         if completion_code.startswith('CQA_'):
#             print(completion_code)
#             print(completion_time)
    
    
# print(Total_Data.head())