# import json
# import random

# def save_filtered_data(filtered_data, file_name):
#     with open(file_name, 'w') as f:
#         json.dump(filtered_data, f, indent=4)

# data_with_answers = json.load(open('filtered_v3.json', 'r'))

# total_change = 0
# total_quetsions = 0

# filtered_data = {}

# for scene in data_with_answers:
#     filtered_data[scene] = {}
#     for change_type in data_with_answers[scene]:
#         qa_list = data_with_answers[scene][change_type]
#         questions = []
#         for d in qa_list:
#             q, a = d.split('Answer:')[0].strip(), d.split('Answer:')[1].strip()
            
#             add = True
#             for c_word in change_type.split(' '):
#                 if a.split(" ")[0].lower() == c_word.lower() and a.split(" ")[0] not in ['Near', 'Next', 'To', 'The', 'Against', 'On', 'Top', 'Of', 'In', 'Front', 'Behind', 'Beside', 'Between', 'Under', 'Below', 'Above', 'Nearby', 'Close', 'By', 'At', 'In', 'The', 'Middle', 'Center', 'Around', 'Another', 'Closer', 'Farther', 'Further', 'Towards', 'Away', 'From', 'Left', 'Right', 'Side', 'Back']:
                    
#                     print('Context Change:', change_type)
#                     print('Question:', q)
#                     print('Answer:', a)
#                     add = False
#                     break
            
#             if add and 'None' not in a and 'No' not in a and 'None.' not in a and 'No.' not in a and 'Zero' not in a and 'Zero.' not in a and '0' not in a and '0.' not in a and 'Nothing' not in a and 'Nothing.' and 'N/A' not in a and 'Not applicable' not in a and 'notable' not in q and 'significant' not in q and 'which objects' not in q and 'what objects' not in q:
#                 if 'color' in q:
#                     prob = random.random()
#                     if prob > 0.7:
#                         questions.append(q)
#                 elif 'shape' in q:
#                     prob = random.random()
#                     if prob > 0.5:
#                         questions.append(q)
#                 else:
#                     questions.append(q)
                    
        
#         if len(questions) > 0:
#             filtered_data[scene][change_type] = questions
#             total_change += 1
#             total_quetsions += len(questions)

# print(len(questions))
# print(f"Total number of changes: {total_change}")
# print(f"Total number of questions: {total_quetsions}")

# save_filtered_data(filtered_data, 'filtered_v4.json')


import json
import random

def save_filtered_data(filtered_data, file_name):
    with open(file_name, 'w') as f:
        json.dump(filtered_data, f, indent=4)
        
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    

# check if a list has two layers:
def check_list(data):
    if isinstance(data, list):
        if isinstance(data[0], list):
            return True
    return False


data = load_json('concise_filtered_v4.json')
raw_data = load_json('filtered_v4.json')

filtered_data = {}
count = 0
for data_key in raw_data:
    filtered_data[data_key] = {}
    for change in raw_data[data_key]:
        try:
            questions = data[change]
            if check_list(questions):
                questions = questions[0]
                
            filtered_data[data_key].update({change: questions})
        except KeyError:
            try:
                questions = data[change.replace('.', '')]
                if check_list(questions):
                    questions = questions[0]
                filtered_data[data_key].update({change: questions})
            except KeyError:
                count += 1
                continue
            
print(count)
        # raw_data[data_key][change] = data[change]
       
save_filtered_data(filtered_data, 'concise_filtered_v5.json')
        