import json
import os
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from collections import deque
import pandas as pd
import numpy as np
import warnings
import re
import numpy as np

json_files = os.listdir('/home/user/shared/solving_data/test_graph')
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

# nx这个库中图的节点必须是可哈希的，所以只能存成tuple格式

def merge(G_input,node):

    # 如果当前选择的node不是tuple类型，则代表当前选择的是一个单节点：
    if not isinstance(node, tuple):
        # 将node（tuple）转化为list之后储存在subgraph
        subgraphs.append(list([node]))
        # nodes是当前学生所有的节点构成的list
        # 找到当前
        json_node = next((t_node for t_node in nodes if t_node['id'] == G.nodes[node]['data'][0]), None)

        # from_id_list 当前节点所有from中包含的数据：即fact的id 注意不是factid
        from_id_list = json_node['from']
        to_id_list = json_node['to']
        # from_facts_id中储存的是这些节点的原节点的from中的节点的factid
        from_facts_id = []
        to_facts_id = []

        # 从from中找到节点，再找到factid
        for from_id in from_id_list:
            t_node_from = next((t_node for t_node in nodes if t_node['id'] == from_id), None)
            from_facts_id.append(t_node_from['factid'])
        for to_id in to_id_list:
            t_node_from = next((t_node for t_node in nodes if t_node['id'] == to_id), None)
            to_facts_id.append(t_node_from['factid'])
        # 其中储存的是每个节点from中的节点的factid，to中的节点的factid，和自己这个节点是由哪些节点合并而成的id
        merge_facts_list.append([sorted(from_facts_id),sorted(to_facts_id),[G.nodes[node]['data'][0]]])

    # 当前选择节点是tuple类型，代表选择的是之前合并过的那个节点
    else:

        subgraphs.append(list(node))

        json_id_list = []

        from_facts_id = []
        to_facts_id = []
        from_id_list = []
        to_id_list = []

        for each_node in list(node):
            # print(each_node)
            json_node = next((t_node for t_node in nodes if t_node['id'] == G.nodes[each_node]['data'][0]), None)
            json_node_id = json_node['id']

            json_id_list.append(json_node_id)
            # print("json_node: ",json_node)

            from_id_list += json_node['from']
            to_id_list += json_node['to']

        from_id_set = set(from_id_list)
        to_id_set = set(to_id_list)
        # 得到合并后结点的id_list,from_list,to_list
        from_id_list = list(from_id_set - to_id_set)

        # to_id_list = list(to_id_set - from_id_set)
        to_id_list = list(to_id_set)
        
        for from_id in list(set(from_id_list)):
            t_node_from = next((t_node for t_node in nodes if t_node['id'] == from_id), None)
            from_facts_id.append(t_node_from['factid'])
        for to_id in to_id_list:
            t_node_from = next((t_node for t_node in nodes if t_node['id'] == to_id), None)
            to_facts_id.append(t_node_from['factid'])
        
        #print(from_facts_id,to_facts_id)
        merge_facts_list.append([sorted(from_facts_id),sorted(to_facts_id),json_id_list])

    # is_forward，is_backward代表向前寻找和向后寻找是否被允许
    # is_backward = False
    # 遍历图中所有node的子节点
    for neighbor in G_input.neighbors(node):
        # 找到从node到这个neighbor的所有路径
        path = list(nx.all_simple_paths(G_input,node,neighbor))
        # 如果路径只有一个，这个就是我们的判断条件
        if len(path) == 1:
            # is_forward向后合并被允许
            # copy一份同样的图，为后面递归做准备
            G_merge_forward = G_input.copy()

            # 将node和neighbor的所有子节点和父节点都提取出来
            connected_to_node = list(G_merge_forward.neighbors(node))
            connected_to_neighbor = list(G_merge_forward.neighbors(neighbor)) 
            parents_to_node = list(G_input.predecessors(node))
            parents_to_neighbor = list(G_input.predecessors(neighbor))
            
            # 图中的每个节点的[data]中储存的内容为这个节点是由哪几个op合并而成的，其中储存的是op节点在原json中的id
            new_data = list(set(G_merge_forward.nodes[node]['data']).union(set(G_merge_forward.nodes[neighbor]['data'])))
            
            node_tuple = node
            neighbor_tuple = neighbor   

            if not isinstance(node, tuple):
                node_tuple = (node,)
            if not isinstance(neighbor, tuple):
                neighbor_tuple = (neighbor,)
            # 新的节点的标注就是node和neighbor合并起来的东西，比如（1，3）和（4）合并称为（1，3，4），这里1，3，4指operation节点在原json的顺序标号  
            new_node_forward = node_tuple + neighbor_tuple
            # 在新的图中增加新的节点，其中data储存了
            G_merge_forward.add_node(new_node_forward, data=new_data)

            # 添加从新节点到所有与node和neighbor相连的节点的边
            for n in set(connected_to_node).union(set(connected_to_neighbor)):
                if n != node and n != neighbor:
                    G_merge_forward.add_edge(new_node_forward, n)
            for n in set(parents_to_node).union(set(parents_to_neighbor)):
                if n != node and n != neighbor:
                    G_merge_forward.add_edge(n,new_node_forward)

            # 删除原来的node和neighbor节点
            G_merge_forward.remove_node(node)
            G_merge_forward.remove_node(neighbor)
            if len(list(G_merge_forward.nodes())) > 2:
                merge(G_merge_forward,new_node_forward)
            # nx.draw(G_merge_forward,with_labels=True)
            # plt.show()

    # 对父节点进行寻找，效果和上面对子节点寻找是一样的
    # for neighbor in G_input.predecessors(node):
    #     path = list(nx.all_simple_paths(G_input,neighbor,node))
    #     if len(path) == 1:
    #         is_backward = True

    #         G_merge_backward = G_input.copy()

    #         connected_to_node = list(G_merge_backward.neighbors(node))
    #         connected_to_neighbor = list(G_merge_backward.neighbors(neighbor)) 
    #         parents_to_node = list(G_input.predecessors(node))
    #         parents_to_neighbor = list(G_input.predecessors(neighbor))
            
    #         new_data = list(set(G_merge_backward.nodes[node]['data']).union(set(G_merge_backward.nodes[neighbor]['data'])))
            
    #         node_tuple = node
    #         neighbor_tuple = neighbor   

    #         if not isinstance(node, tuple):
    #             node_tuple = (node,)
    #         if not isinstance(neighbor, tuple):
    #             neighbor_tuple = (neighbor,)
    #         new_node_backward = neighbor_tuple + node_tuple  

    #         G_merge_backward.add_node(new_node_backward, data=new_data)

    #         # 添加从新节点到所有与node和neighbor相连的节点的边
    #         for n in set(connected_to_node).union(set(connected_to_neighbor)):
    #             if n != node and n != neighbor:
    #                 G_merge_backward.add_edge(new_node_backward, n)
    #         for n in set(parents_to_node).union(set(parents_to_neighbor)):
    #             if n != node and n != neighbor:
    #                 G_merge_backward.add_edge(n,new_node_backward)

    #         # 删除原来的node和neighbor节点
    #         G_merge_backward.remove_node(node)
    #         G_merge_backward.remove_node(neighbor)

            # nx.draw(G_merge_backward,with_labels=True)
            # plt.show()
    
    # 如果满足我们的要求而且新的图仍然有合并的意义，我们再使用递归进行合并

    # if is_backward and len(list(G_merge_backward.nodes())) > 2:
    #     merge(G_merge_backward,new_node_backward)

# 储存所有合并的点的信息
all_merge_data = []
# 储存每个学生都有多少个节点，例如[12,24,34,132,23]代表5个学生分别有这么多节点
student_id_length = []

json_files = sorted(json_files)
print(len(json_files))
for json_file in json_files:
    connected_operations = {}
    if not json_file.endswith('.json'):
        continue
    if json_file[0].isdigit() == False:
        continue
    # if json_file != '5_result.json':
    #     continue

    # print(json_file)

    # 子图
    subgraphs = []
    merge_facts_list = []
    #定义图结构
    G = nx.DiGraph()

    with open(f'/home/user/shared/solving_data/test_graph/{json_file}', 'r') as file:

        data = json.load(file)
        # print(data)
        nodes = data['nodes']
        student_id_length.append(len(nodes))

        # 把json中所有op的节点都提取出来
        operations = {node['id']: node for node in nodes if node['type'] == 'operation'}
        # 确定两个相邻的op
        for operation_id,operation_node in operations.items():
            for to_id in operation_node['to']:
                for other_operaion_id,other_operation_node in operations.items():
                    if operation_id!=other_operaion_id and to_id in other_operation_node['from']:
                        if operation_id in connected_operations:
                            connected_operations[operation_id].add(other_operaion_id)
                        else:
                            connected_operations[operation_id] = set([other_operaion_id])

        # 在图中添加节点和边
        for i, (operation_id,operation_node) in enumerate(operations.items()):
            G.add_node(i,data=[operation_node['id']])
        for i, (operation_id, connected_ids) in enumerate(connected_operations.items()):
            for node1 in G.nodes():
                for node2 in G.nodes():
                    if node1 != node2 and G.nodes[node1]['data'][0] == operation_id and G.nodes[node2]['data'][0] in connected_ids:
                        G.add_edge(node1, node2)

        # 遍历所有的节点，并对每个节点进行合并尝试
        nodelist = list(G.nodes())
        for node in nodelist:
            ## modified
            if len(list(G.nodes())) > 2:
                merge(G, node)
    
    all_merge_data.append(merge_facts_list) 
print("len",len(all_merge_data))
# print(all_merge_data[0])
#将all_merge_data中的数据化成一张表格，其中横是对应的文件编号，纵是每个[from_fact_id,to_fact_id,operation_id]的列表中的[from_fact_id,to_fact_id]的组合

# 用于输出csv文件的column储存
data_column_output = []

data_column_search = []
from_student_id = []

# df是一个5行n列的表，每一列代表我们找到的pair，其格式为字符串，每一行代表一个学生，如果这个学生出现了这个pair，那么交叉格为1，否则为0
# 最后一行表示这个pair具体在哪几个学生中出现过
df = pd.DataFrame(index=range((len(json_files))))
print(df)



for i, merge_data in enumerate(all_merge_data): 
    for data in merge_data:
        from_facts = sorted(data[0])
        to_facts = sorted(data[1])

        new_column_output = str(tuple(from_facts)) + str(tuple(to_facts))
        new_column = [from_facts,to_facts]
        if new_column_output not in set(data_column_output):
            data_column_output.append(new_column_output)
            data_column_search.append(new_column)

            df[new_column_output] = [1 if t == i else 0 for t in range(len(all_merge_data))]
            from_student_id.append(set([i]))
        else:
            df.loc[i,new_column_output] = 1
            from_student_id[data_column_output.index(new_column_output)].add(i)
df.to_csv('/home/user/shared/solving_data/data/merge.csv')
# 输出一个json文件作为查找表，里面储存了每个pair是由哪个同学的哪些op合并起来的
search_operation = {}
# 储存了每个pair是从哪个同学产生的，长度与pair去重后的长度相同，例如[0,0,0,1,1,1,2,2,3,3,3,4,4]这样
from_student_id_list = []

for column in data_column_output:
    for i, merge_data in enumerate(all_merge_data):
        for data in merge_data:
            
            need_continue = False

            from_facts = sorted(data[0])
            to_facts = sorted(data[1])
            operation_id = data[2]

            # 将集合转换为元组
            matches1 = re.findall(r'\(.*?\)', column)
            column_set = [tuple(eval(match)) for match in matches1]  

            if set(from_facts) == set(column_set[0]) and set(to_facts) == set(column_set[1]):
                
                pair_id = data_column_search.index([from_facts,to_facts]) 
                # 检查键是否存在，如果不存在，先创建一个空字典
                # print("pair",pair_id)
                if pair_id not in search_operation:
                    search_operation[pair_id] = [] 
                
                for item in search_operation[pair_id]:
                    if item.get("student_id") == i:
                        need_continue = True
                
                if need_continue == True:
                    continue
                        
                if search_operation[pair_id] == []:
                    from_student_id_list.append(i)

                search_operation[pair_id].append({'student_id':i,'operation_id':tuple(operation_id)})

print(from_student_id_list)
# from_student_id_list储存了每个pair率先在哪个学生里被发现了
np.save("/home/user/shared/solving_data/data/from_student_id_list.npy",np.array(from_student_id_list))

with open('/home/user/shared/solving_data/data/search_operation.json', 'w') as f:
    json.dump(search_operation, f, indent=4)
# search_op中key为pairid，value为各个stuid及其中的op组合

df.loc[len(df)] = from_student_id

#将csv保存下来
df.to_csv('/home/user/shared/solving_data/data/merge_data.csv')


column=["in","out"]+[str(i + 1) for i in range(len(json_files))] + [str(i + 1) + "_op" for i in range(len(json_files))]
#按照覆盖规则输出一个覆盖表
same_in_df = pd.DataFrame(columns =column)

for column_name in data_column_output:
    # 从字符串转化到元组构成的集合
    matches1 = re.findall(r'\(.*?\)', column_name)
    set1 = [set(eval(match)) for match in matches1]
    print("look set",set1)
    initial_row = [list(set1[0]), list(set1[1])] + [[] for _ in range(len(json_files) * 2)]
    print("same_in_df",len(same_in_df))
    same_in_df.loc[len(same_in_df),column] = initial_row

    for other_column in data_column_output:

        matches2 = re.findall(r'\(.*?\)', other_column)
        set2 = [set(eval(match)) for match in matches2]
        # 输入相同，输出set2是set1子集（set1对则set2对）
        if set1[0] == set2[0] and set1[1] >= set2[1]:
            # 找到当前的是第几个pair
            pair_id = data_column_search.index([sorted(list(set2[0])),sorted(list(set2[1]))])
            print("len(df)",len(df))
            id_list = list(df.loc[len(df)-1,other_column])
            # 其中存的是other_column对应的那个merge结点对应在哪些学生id出现过
            print("look id_list",id_list)
            # 从存下来的json查找表中找到组合成这个被覆盖的pair的op都是哪些，把这些储存下来
            for i in id_list:
                for student in search_operation[pair_id]:
                    if student["student_id"] == i:
                        operation_id = student["operation_id"]
                same_in_df.loc[len(same_in_df)-1,str(i+1)].append(operation_id)
                ## 表示这个merge后的结点是由某个学生的哪几个op合并起来的
print(len(same_in_df))
# 对上面所有的单元格进行合并，取每个格子中的并集
for i in range(len(same_in_df)):
    for j in range(1,len(json_files)+1):
        total_list = same_in_df.loc[i,str(j)]
        print("total_list",total_list)
        union_set = set().union(*total_list)
        # print(total_list,union_set)
        same_in_df.loc[i,str(j)] = union_set

# *_op列的每一行储存的是这个pair如果被批改的话，被覆盖的pair的op在这个学生总op的占比
# 可以简单理解成批每个pair能够给我们带来的增益，后面可能会用到这个数据
for i in range(len(same_in_df)):
    for j in range(1,len(json_files)+1):
        same_in_df.loc[i,str(j)+"_op"] = len(same_in_df.loc[i,str(j)])/student_id_length[j-1]

# print(same_in_df)
same_in_df.to_csv('/home/user/shared/solving_data/data/same_in_df_right.csv')





            
            













                    
                








