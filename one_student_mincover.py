# to be modified
# 寻找最大覆盖学生的那个函数需要修改
# 初步想法是重写代码

import pandas as pd
import os
import json
import ast
import numpy as np

with open("/home/user/shared/solving_data/data/same_in_df_right.csv") as f:
    data_same_in = pd.read_csv(f)
# pair op的并集 占比
from_student_id_list = np.load("/home/user/shared/solving_data/data/from_student_id_list.npy", allow_pickle=True)

json_files = os.listdir('/home/user/shared/solving_data/test_graph')
json_files = sorted(json_files)
# ??没太看明白
# student_nodes=[0,0,0,0,0]
student_nodes = []
for i in range(len(json_files)):
    student_nodes.append([])
print(len(json_files))
for json_file in json_files:
    if not json_file.endswith(".json"):
        continue
    if json_file[0].isdigit() == False:
        continue
    print("in")
    with open(f'/home/user/shared/solving_data/test_graph/{json_file}', 'r') as file:
        data = json.load(file) 
        print("look",json_file[0])
        nodes = data["nodes"]
        student_node = [node['id'] for node in nodes if node['type'] == 'operation']
        print(json_file[0])
        student_nodes[int(json_file[0])-1] = student_node

print("student_node",student_nodes)

with open("/home/user/shared/solving_data/data/search_operation.json") as f:
    json_data = json.load(f)
# search_operation[pair_id].append({'student_id':i,'operation_id':tuple(operation_id)})
# key:pair_id value 出现这个pair的学生以及是由哪几个op组合而成

# 先找到能够覆盖其他学生的op的最多的那个学生
def get_max_cover_from_one_student(student_n,pair_json):
    max_cover_num = 0
    max_cover_student_id = []
    max_cover_list = []
    coverd_pair_id_list = []
    for i in range(len(student_n)):
        cover_list = [set([]) for t in range(len(student_n))]
        for pair_id, pair_from in pair_json.items():
            is_from_this_student = False
            for item in pair_from:
                if item["student_id"] == i:
                    is_from_this_student = True
            if is_from_this_student:
                for item in pair_from:
                    cover_list[item["student_id"]] = cover_list[item["student_id"]].union(set(item["operation_id"])) 
        sum_cover_num = 0
        for coverd_node in cover_list:
            sum_cover_num += len(coverd_node)
        if sum_cover_num > max_cover_num:
            max_cover_num = sum_cover_num
            max_cover_student_id.append(i)
            max_cover_list = cover_list
    for i in range(len(from_student_id_list)):
        if from_student_id_list[i] in max_cover_student_id:
            coverd_pair_id_list.append(i)

    return max_cover_student_id, max_cover_list, coverd_pair_id_list
# [0,1,3,5]
# 第一项为一个list，表示max_cover依次增大的student
# coverd_pair_id_list表示这个list能覆盖多少pair
# max_cover_list表示这个最大的学生能覆盖各个学生的多少op

# 在选取好了第一个学生之后还需要选择哪些pair才能够最高效的对所有的op进行覆盖，有点像一个特殊的最小覆盖问题
# 不过这一条暂时舍弃，我们应该不会给老师呈现pair让老师去批改
def get_max_cover_node(student_nodes, covered_pair_id_list, covered_node_list, choosen_student_id_list,dataset):
    max_cover_num = 0
    result_list = []

    for pair_id in range(len(dataset)):
        covered_num = 0
        temp_covered_node_list = [set([]) for t in range(len(student_nodes))]
        if pair_id in covered_pair_id_list:
            continue
        for i in range(len(student_nodes)):
            if i in choosen_student_id_list:
                continue
            for operation_id in ast.literal_eval(dataset.loc[pair_id, str(i+1)]):
                if operation_id in covered_node_list[i]:
                    continue
                else:
                    temp_covered_node_list[i].add(operation_id)
                    covered_num += 1
        if covered_num > max_cover_num:
            max_cover_num = covered_num
            result_list.clear()
            result_list.append(pair_id)
        elif covered_num == max_cover_num:
            result_list.append(pair_id) 
    return result_list

# 按顺序比较类似[[],[]]
def check_same(list1,list2):
    is_same = True
    for i in range(len(list1)):
        if set(list1[i]) != set(list2[i]):
            is_same = False
            break
    return is_same

def find_difference(list1,list2):
    result_list = []
    for item in list1:
        if item not in list2:
            result_list.append(item)
    return result_list

student_id_list, covered_operation_id_list, covered_pair_list =  (get_max_cover_from_one_student(student_nodes,json_data))
initial_list = covered_pair_list

print(initial_list)

## 直到完全覆盖
while not check_same(covered_operation_id_list,student_nodes) :
    min_sum_pair_id = []
    min_sum = 999
    choose_pair_id = get_max_cover_node(student_nodes, covered_pair_list, covered_operation_id_list, student_id_list, data_same_in)
    for pair_id in choose_pair_id:
            sum_in_and_out = len(ast.literal_eval(data_same_in.loc[pair_id,'in'])) + len(ast.literal_eval(data_same_in.loc[pair_id,'out']))
            if sum_in_and_out < min_sum:
                min_sum = sum_in_and_out
                min_sum_pair_id.clear()
                min_sum_pair_id.append(pair_id)
            elif sum_in_and_out == min_sum:
                min_sum_pair_id.append(pair_id)
    if len(min_sum_pair_id)>0:
        covered_pair_list.append(min_sum_pair_id[0])
        for i in range(len(student_nodes)):
            covered_operation_id_list[i] = covered_operation_id_list[i].union(set(ast.literal_eval(data_same_in.loc[min_sum_pair_id[0], str(i+1)])))


print("pair_id_list",covered_pair_list)  
print(find_difference(initial_list, covered_pair_list))  