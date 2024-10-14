import json
import random

# filtered_data = json.load(open('filtered_v4.json', 'r'))

# final_data ={}
# for scene in filtered_data:
#     final_data[scene] = {}
#     for change_type in filtered_data[scene]:
#         filtered_questions = []
#         questions = list(set(filtered_data[scene][change_type]))
        
#         for q in questions:
#             if 'color' in q:
#                 remove_prob = random.random()        
#                 if remove_prob > 0.7:
#                     filtered_questions.append(q)
                    
#             elif 'shape' in q:
#                 remove_prob = random.random()
#                 if remove_prob > 0.5:
#                     filtered_questions.append(q)
#             else:
#                 filtered_questions.append(q)
                
#         final_data[scene][change_type] = filtered_questions
        
    
# save the filtered data    
# with open('filtered_v5.json', 'w') as f:
#     json.dump(final_data, f, indent=4)


data = json.load(open('filtered_v6.json', 'r'))
backup = json.load(open('total_merged_data.json', 'r'))

total_change = 0
total_quetsions = 0

filtered_data = {}
for scene in data:
    filtered_data[scene] = {}
    for change_type in data[scene]:
        filtered_questions = []
        if len(data[scene][change_type]) == 0 or len(backup[scene][change_type]) == 0:
            continue
        else:
            for question in data[scene][change_type]:
                if 'notable' in question or 'significant' in question or 'what objects' in question or 'which objects' in question:
                    continue
                else:
                    filtered_questions.append(question)
                    total_quetsions += 1
            filtered_data[scene][change_type] = filtered_questions
        
print(f"Total number of changes: {total_change}")
print(f"Total number of questions: {total_quetsions}")

with open('filtered_v8.json', 'w') as f:
    json.dump(filtered_data, f, indent=4)

# backup = json.load(open('total_merged_data.json', 'r'))

# need_add = 0
# filtered_data = {}
# total_change = 0

# for scene in data:
#     filtered_data[scene] = {}
#     for change_type in data[scene]:
#         print(f"Scene: {scene}, Change type: {change_type}, Number of questions: {len(data[scene][change_type])}")
#         questions = list(set(data[scene][change_type]))
#         remain = 5 - len(questions)
            
#         if len(backup[scene][change_type]) >= 5:
#             total_change +=1
#             while remain > 0:
#                 question = random.choice(backup[scene][change_type])
#                 if question not in questions:
#                     questions.append(question)
#                     remain -= 1
                    
#             filtered_data[scene][change_type] = questions
                    
# with open('filtered_v7.json', 'w') as f:
#     json.dump(filtered_data, f, indent=4)

        
            
            
            
                
                
    
    
        
        