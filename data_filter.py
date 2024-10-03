import os
import json
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load the data
# data = json.load(open('context_changes_human/filtered_total_change.json', 'r'))

# print(f"Total keys: {len(data.keys())}")

# changes = []
# key_mapping = []  # Store the key associated with each change

# # Extract changes and keep track of which key each change belongs to
# for k in data.keys():
#    for i in data[k]:
#        changes.append(i)
#        key_mapping.append(k)  # Add the key corresponding to this change

# # 1. Load a pretrained Sentence Transformer model
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # 2. Calculate embeddings for the changes
# embeddings = model.encode(changes)
# print(f"Embeddings shape: {embeddings.shape}")

# # 3. Compute the cosine similarity matrix
# cosine_similarities = util.pytorch_cos_sim(embeddings, embeddings)

# # 4. Define a similarity threshold
# similarity_threshold = 0.8

# # 5. List to store indices of changes to keep
# keep_indices = []

# # 6. Iterate through each pair of sentences to filter based on similarity
# for i in range(len(changes)):
#     is_similar = False
#     for j in range(i):
#         if cosine_similarities[i][j] > similarity_threshold:
#             is_similar = True
#             break
#     if not is_similar:
#         keep_indices.append(i)

# # 7. Filter the changes and map them back to their original keys
# filtered_changes = [changes[i] for i in keep_indices]
# filtered_keys = [key_mapping[i] for i in keep_indices]

# # Output the filtered changes with their original keys
# print(f"Original number of changes: {len(changes)}")
# print(f"Number of changes after filtering: {len(filtered_changes)}")

# filtered_data = {}
# for key, change in zip(filtered_keys, filtered_changes):
#     if key not in filtered_data:
#         filtered_data[key] = []
#     filtered_data[key].append(change)


# Output the filtered changes and their corresponding keys
# save the filtered changes
# with open('context_changes_human/non_similar_filtered_total_change.json', 'w') as file:
#     json.dump(filtered_data, file, indent=4)

def summarize_changes(json_data):
    # Initialize a dictionary to store the total counts for each change category
    total_changes = {
        "Object Movement Change": 0,
        "Object Addition Change": 0,
        "Object Removal Change": 0,
        "Object Replacement Change": 0,
        "Object Attribute Change": 0
    }
    
    # Iterate through each scene
    for scene_id, changes in json_data.items():
        # Iterate through each change category in the scene
        for category, descriptions in changes.items():
            # Add the count of descriptions in the current category to the total
            total_changes[category] += len(descriptions)
    
    return total_changes

import matplotlib.pyplot as plt
filtered_data = json.load(open('context_changes_human/category_non_similar_filtered_total_change.json', 'r'))

summarize_change = summarize_changes(filtered_data)

print(summarize_change)
print(sum(summarize_change.values()))


# Output filtered changes and their corresponding keys

# for key, change_list in filtered_data.items():
#     print(f"Key: {key}")
#     for change in change_list:
#         print(f"  - {change}")

change_counts = {scene_id: sum(len(descriptions) for descriptions in changes.values()) for scene_id, changes in filtered_data.items()}
total_changes = sum(change_counts.values())
print(f"Total number of changes: {total_changes}")

# Collect scene ids with <= 10 changes
scene_ids_with_ten_or_fewer_changes = [scene_id for scene_id, count in change_counts.items() if count <= 10]

# Output the result
print("Scenes with 10 or fewer changes:")
print(scene_ids_with_ten_or_fewer_changes)
print(f"Number of scenes with <= 10 changes: {len(scene_ids_with_ten_or_fewer_changes)}")

# Create a bar chart to show the number of changes at different keys (scene ids)
# plt.figure(figsize=(10, 6))
# plt.bar(change_counts.keys(), change_counts.values(), color='blue')
# plt.title('Number of Changes per Scene ID')
# plt.xlabel('Scene ID')
# plt.ylabel('Number of Changes')
# plt.xticks(rotation=45)
# plt.grid(axis='y')
# plt.tight_layout()

# plt.show()

