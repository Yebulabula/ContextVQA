
# import plotly.graph_objects as go
# import os
# import numpy as np
# import json
# import firebase_admin
# from firebase_admin import credentials, firestore
# import base64
# import random




# if firebase_credentials:
#     # Decode the base64 encoded credentials
#     cred_json = base64.b64decode(firebase_credentials).decode('utf-8')
#     cred_dict = json.loads(cred_json)
#     cred = credentials.Certificate(cred_dict)

#     # Initialize Firebase app if not already initialized
#     if not firebase_admin._apps:
#         firebase_admin.initialize_app(cred)

#     # Set up Firestore client
#     db = firestore.client()

#     def export_firestore_collection_to_json(collection_name, output_file):
#         # Reference to the Firestore collection
#         collection_ref = db.collection(collection_name)
        
#         # Get all documents in the collection
#         docs = collection_ref.stream()

#         # Prepare a dictionary to hold the exported data
#         data = {}

#         # Iterate over documents and collect data
#         for doc in docs:
#             data[doc.id] = doc.to_dict()

#         # Write data to a JSON file
#         with open(output_file, 'w') as f:
#             json.dump(data, f, indent=2)


#     # Example: Export data from 'your-collection-name' to 'output.json'
#     collection_name = 'ContextReason'
#     output_file = 'outputs.json'

#     export_firestore_collection_to_json(collection_name, output_file)

import json
import numpy as np
import os

with open('outputs.json', 'r') as f:
    data = json.load(f)
    
    
print(len(data))  # Number of documents in the collection

scene_occurence = {}
answers = []
for d in data.values():
    scene_id = d['scene_id']
    if scene_id in scene_occurence:
        scene_occurence[scene_id] += 1
    else:
        scene_occurence[scene_id] = 1
    answers.append(d['answer'])
    
yes_no_answers = [a for a in answers if 'yes' in a or 'no' in a or 'Yes' in a or 'No' in a]

scene_occurence = {k: v for k, v in sorted(scene_occurence.items(), key=lambda item: item[1], reverse=True)}
print(scene_occurence)  # Number of occurences of each scene_id
print(f'There are {len(yes_no_answers)} yes/no answers in the collection of {len(answers)}')  # Number of yes/no answers