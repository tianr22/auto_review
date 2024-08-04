# TODO process data for backend
import json
from pipeline import Info,get_all_student_json_files
import os
from functools import reduce
# DONE
# TO BE CHECKED
def get_subgraph(factid,json_dic_path,json_file_path):
    with open(json_dic_path+json_file_path,'r') as file:
        data=json.load(file)
        nodes=data['nodes']
        final_node=[node for node in nodes if node['type']=='fact' and node['factid']==factid]
        assert len(final_node)==1
        fact_list=[final_node['id']]
        searched_fact_list=[]
        searched_op_list=[]
        while True:
            searched_fact_list.extend(fact_list)
            from_op_nodes=[node for node in nodes if node['type']=='operation' and any([fact in node['to'] for fact in fact_list])]
            if len(from_op_nodes)==0:
                break
            searched_op_list.extend(from_op_nodes)
            searched_op_list=list(set(searched_op_list))
            fact_list=list(set(sum([node['from'] for node in from_op_nodes],[]))-set(searched_fact_list))
            if len(fact_list)==0:
                break
        return searched_fact_list,searched_op_list
    

# DONE
# TO BE CHECKED
def check_subgraph_correctness(store_path,json_dic_path,json_file_path,searched_fact_list,searched_op_list):
    info=Info.load_from_json(store_path)
    fact_info = info.fact_info
    operation_right = info.operation_right
    json_files=os.listdir(json_dic_path)
    json_files=[json_file for json_file in json_files if json_file.endswith(".json") and json_file[0].isdigit()]
    json_files=sorted(json_files)
    index=json_files.index(json_file_path)
    with open(json_dic_path+json_file_path,'r') as file:
        data=json.load(file)
        nodes=data['nodes']
        selected_fact_ids=[node['factid'] for node in nodes if node['type']=='fact' and node['id'] in searched_fact_list]
        if all(fact_info[selected_fact_id]==1 for selected_fact_id in selected_fact_ids) and all(op_node in operation_right[index] for op_node in searched_op_list):
            return True
        else:
            return False
        

def get_fact_id(student_fact,json_dic_path,json_file_path):
    with open(json_dic_path+json_file_path,'r') as file:
        data=json.load(file)
        nodes=data['nodes']
        for node in nodes:
            if node['id'] == student_fact:
                return node['factid']
        return None

def intersection(fact_id,json_dic_path):
    json_files = get_all_student_json_files(json_dic_path)
    ## 在这里简单地使用json_files这个列表来对应学生学号
    ## 例如，json_files[0]对应学号为0的学生
    ## TO BE MODIFIED
    ## 后续需要确定学号的真实对应关系
    include_student_id_list = []
    subgraph_list = []
    for index,json_file in enumerate(json_files):
        is_include = False
        with open(json_dic_path+json_file,"r") as file:
            data = json.load(file) 
            nodes=data['nodes']
            fact_nodes = [node for node in nodes if node['type']=='fact']
            if any([fact_node['factid']==fact_id for fact_node in fact_nodes]):
                is_include = True
                include_student_id_list.append(index)
                searched_fact_list,_ = get_subgraph(fact_id,json_dic_path,json_file)
                searched_fact_id_list=set([get_fact_id(student_fact,json_dic_path,json_file) for student_fact in searched_fact_list])
                subgraph_list.append(searched_fact_id_list)

    # 求最大交集
    max_intersection = reduce(set.intersection, subgraph_list)
    ## 返回包含这个fact_id的所有学生index和最大交集
    return include_student_id_list,max_intersection


## TODO K-means
def classify():
    pass
