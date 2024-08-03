# TODO process data for backend
import json
from pipeline import Info
import os

# DONE
# TO BE CHECKED
def get_subgraph(factid,json_file_path):
    with open(json_file_path,'r') as file:
        data=json.load(file)
        nodes=data['nodes']
        final_node=[node for node in nodes if node['type']=='fact' and node['factid']==factid]
        assert len(final_node)==1
        fact_list=[final_node]
        searched_fact_list=[]
        searched_op_list=[]
        while True:
            searched_fact_list.extend(fact_list)
            from_op_nodes=[node for node in nodes if node['type']=='operation' and any([fact in node['to'] for fact in fact_list])]
            searched_op_list.extend(from_op_nodes)
            searched_op_list=list(set(searched_op_list))
            if len(from_op_nodes)==0:
                break
            fact_list=list(set(sum([node['from'] for node in from_op_nodes],[])))-set(searched_fact_list)
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
        
            
            