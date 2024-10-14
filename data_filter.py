import matplotlib.pyplot as plt
import json

filtered_data = json.load(open('context_changes_human/category_non_similar_filtered_total_change.json', 'r'))

def remove_duplicates(json_data):
    # Iterate through each key in the JSON data
    for key in json_data:
        for change_type in json_data[key]:
            # Remove duplicates by converting the list to a set and back to a list
            json_data[key][change_type] = list(set(json_data[key][change_type]))
    return json_data

filtered_data = remove_duplicates(filtered_data)

num_changes = 0
for key in filtered_data:
    for change_type in filtered_data[key]:
        num_changes += len(filtered_data[key][change_type])
        
print(f"Total number of changes: {num_changes}")
# save the filtered data
with open('context_changes_human/category_non_similar_filtered_total_change.json', 'w') as f:
    json.dump(filtered_data, f, indent=4)