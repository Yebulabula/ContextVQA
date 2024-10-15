
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
    collection_name = 'Answer'
    output_file = 'ContextQA_data.json'

    export_firestore_collection_to_json(collection_name, output_file)

# print(answers)
# for a in answers:
#     print(a)    
# yes_no_answers = [a for a in answers if 'yes' in a or 'no' in a or 'Yes' in a or 'No' in a]

# scene_occurence = {k: v for k, v in sorted(scene_occurence.items(), key=lambda item: item[1], reverse=True)}
# print(scene_occurence)  # Number of occurences of each scene_id
# print(f'There are {len(yes_no_answers)} yes/no answers in the collection of {len(answers)}')  # Number of yes/no answers


# # long_changes =[]
# # with open('new_user.json', 'r') as f:
# #     data = json.load(f)
# #     for d in data.values():
# #         if len(d['context_change']) > 70:
# #             long_changes.append(d['context_change'])

# # with open('outputs.json', 'r') as f:
# #     data = json.load(f)
# #     for d in data.values():
# #         if len(d['context_change']) > 70:
# #             long_changes.append(d['context_change'])
            
            
# # with open('context_data.json', 'r') as f:
# #     data = json.load(f)
# #     for d in data:
# #         if len(d['context_change']) > 70:
# #             long_changes.append(d['context_change'])
            
# # with open('/mnt/new_drive/Documents/3D-VLM/SQA3D/gpt4o_contexts.json', 'r') as f:
# #     data = json.load(f)
# #     for d in data:
# #         for item in d['generated_context']["Geometric Changes"]:
# #             if len(item) > 70:
# #                 long_changes.append(item)
                
# #         for item in d['generated_context']["Addition and Removal Changes"]:
# #             if len(item) > 70:
# #                 long_changes.append(item)

# # long_questions = []

# # valid_start_words = ['Do', 'Does', 'What', 'Which', 'How', 'Where', 'When', 'Who', 'Why', 'Are', 'Is', 'Can', 'Could', 'Should', 'Would', 'Will', 'Have', 'Has', 'Had', 'May', 'Might', 'Must', 'Shall', 'Were', 'Am']

# # with open('/mnt/new_drive/Documents/3D-VLM/Chat-3D-v2/annotations/scanqa/ScanQA_v1.0_test_w_obj.json', 'r') as f:
# #     data = json.load(f)
# #     for d in data:
# #         if len(d['question']) > 30 and d['question'].split()[0] in valid_start_words:
# #             long_questions.append(d['question'])
            
# # # with open('/mnt/new_drive/Documents/3D-VLM/Chat-3D-v2/annotations/scanqa/ScanQA_v1.0_val.json', 'r') as f:
# # #     data = json.load(f)
# # #     for d in data:
# # #         if len(d['question']) > 30 and d['question'].split()[0] in valid_start_words:
# # #             long_questions.append(d['question'])
# # # print(len(long_changes))  # Number of documents with long context changes

# # long_questions = list(set(long_questions))
# import json

# # # save long changes
# # json.dump(long_questions, open('quetions_inspirations.json', 'w'), indent=2)


# movement_descriptions = json.load(open('movement_changes.json', 'r'))

# movement_descriptions_0 = {k: v for k, v in sorted(movement_descriptions.items(), key=lambda item: item[0]) if k.startswith('scene')}

# movement_descriptions_1 = {k: v for k, v in sorted(movement_descriptions.items(), key=lambda item: item[0]) if not k.startswith('scene')}

# total_movement_descriptions = {**movement_descriptions_0, **movement_descriptions_1}

# print(movement_descriptions)

# json.dump(total_movement_descriptions, open('movement_changes.json', 'w'), indent=2)

# addition_descriptions = json.load(open('addition_changes.json', 'r'))

# add_changes = []
# for scene in addition_descriptions:
#     changes = addition_descriptions[scene]

#     print(scene)
#     for change in changes:
#         if 'add' in change and 'remove' not in change and 'replace' not in change:
#            add_changes.append(change)

# # save them it text file
# with open('addition.txt', 'w') as f:
#     for change in add_changes:
#         f.write(change + '\n')

# json.dump(total_addition_descriptions, open('attribute_changes.json', 'w'), indent=2)