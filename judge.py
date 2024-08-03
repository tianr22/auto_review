# to be checked


import json
import numpy as np
import os
import pandas as pd
import ast

# 记录所有 fact 的正误，1代表正确，0代表错误,-1代表未知
## to be modified
fact_correct = [1,1,1,1,1,
                1,1,1,1,1,
                1,1,0,1,1,
                1,1,1,1,0,
                1,1,1,0,1,
                0,0,1,0,0]
# fact_correct = [1 for i in range(30)]
# 记录每个人当前operation的状态
operation_right = [[4,7,10,13,15,17,19,23,25,29,33]]
operation_wrong = [[31]]
json_files = os.listdir('/home/user/shared/solving_data/test_graph')
json_files = sorted(json_files)
# 4 = [0,0,0,0,0]
student_nodes = []
for i in range(len(json_files)):
    student_nodes.append(0)
for i in range(len(json_files)-1):
    operation_right.append([])
    operation_wrong.append([])
# 通过fact更新所有的operation的正误
# 原则是如果输入都对，但是输出包含错误信息，则op错
# 如果输出都对，输入包含错误信息，则op错
# 但是如果输入输出都包含错误，则无法判断，需要老师进行矫正

for json_file in json_files:
    if not json_file[0].endswith(".json"):
        continue
    if json_file[0].isdigit() == False:
        continue
    cur_student = int(json_file[0]) - 1
    print(json_file)
    with open(f'/home/user/shared/solving_data/test_graph/{json_file}', 'r') as file:
        data = json.load(file)
        nodes = data["nodes"]

        for node in nodes:
            if node['type'] == 'operation':
                is_from_correct = True
                is_to_correct = True
                for from_id in node['from']:
                    for from_node in nodes:
                        if from_node == node:
                            continue
                        if from_node["id"] == from_id:
                            # 如果这个fact正确，略过
                            if fact_correct[from_node["factid"]-1] == 1:
                                continue
                            # 如果这个fact错误，说明from中存在错误的fact
                            elif fact_correct[from_node["factid"]-1] == 0:
                                is_from_correct = False
                                break
                for to_id in node['to']:
                    for to_node in nodes:
                        if from_node == node:
                            continue
                        if to_node["id"] == to_id:
                            if fact_correct[to_node["factid"]-1] == 1:
                                continue
                            elif fact_correct[to_node["factid"]-1] == 0:
                                is_to_correct = False
                                break        
                
                # 如果输入和输出只有一端出错，那么这个op应该是错误的
                if is_from_correct != is_to_correct:
                    if node["id"] not in operation_wrong[cur_student]:
                        operation_wrong[cur_student].append(node["id"])
        
        student_node = [node['id'] for node in nodes if node['type'] == 'operation']
        student_nodes[int(json_file[0])-1] = student_node

print(operation_wrong)

def find_difference(list1,list2,list3):
    result_list = []
    for i in range(len(list1)):
        remain = set(list1[i]) - set(list2[i]) - set(list3[i])
        result_list.append((remain))
    return result_list

from_student_id_list = np.load('/home/user/shared/solving_data/data/from_student_id_list.npy')
                                 
# 根据现在的operation的正误，更新pair的正误
with open("/home/user/shared/solving_data/data/same_in_df_right.csv") as f:
    data_same_in = pd.read_csv(f)

with open("/home/user/shared/solving_data/data/same_out_df_wrong.csv") as f:
    data_same_out = pd.read_csv(f)

pair_correct = [0 for i in range(len(data_same_in))]

print(operation_right)
# print(pair_correct)

# 对data_same_in进行遍历
for pair_id in range(len(data_same_in)):
    # if pair_correct[pair_id] == 0:
    #     continue

    from_student_id = from_student_id_list[pair_id]
    cover_data = data_same_in.loc[pair_id, str(from_student_id + 1)]

    if cover_data == "set()":
        continue
    else:
        cover_data = ast.literal_eval(data_same_in.loc[pair_id, str(from_student_id + 1)])

    is_pair_correct = True
    # 遍历每个pair的所有op，如果这个op不在对的op的list中，则这个pair为错误的
    for operation_id in cover_data:
        if operation_id in operation_right[from_student_id]:
            continue
        else:
            is_pair_correct = False
            break
    
    if is_pair_correct == True:
        pair_correct[pair_id] = 1

    in_data = ast.literal_eval(data_same_in.loc[pair_id,"in"])
    out_data = ast.literal_eval(data_same_in.loc[pair_id,"out"])
        
    for i in range(len(operation_right)):
        if i == from_student_id:
            continue
        check_data = data_same_in.loc[pair_id, str(i + 1)]
        if check_data == "set()":
            continue
        else:
            check_data = ast.literal_eval(check_data)

        print(check_data)

        with open("/home/user/shared/solving_data/test_graph/" + str(i+1) + "_result.json") as f:
            student_data = json.load(f)

        # 如果这个被覆盖的节点是单个op，则pair对，被覆盖的op就对
        for each_node in student_data["nodes"]:
            if each_node["id"] in check_data:

                fact_id_list = []
                for other_node in student_data["nodes"]:
                    if other_node == each_node:
                        continue   
                    if other_node["id"] in each_node["from"]:
                        fact_id_list.append(other_node["factid"])
                
                if set(fact_id_list) == set(in_data):
                    if each_node["id"] not in operation_right[i]:
                        operation_right[i].append(each_node["id"])
                        
                

print("模拟批完第一个人之后对的op：",operation_right)
# print(pair_correct)
print("模拟批完第一个人之后错的op：",operation_wrong)

print("还剩下哪些op没有被批改：",find_difference(student_nodes, operation_right, operation_wrong))

sum = 0
for i in range(len(student_nodes)):
    sum += len(student_nodes[i])        