# TODO process data for backend
import json
def classify_meta_graph():
    pass

def classify_graph():
    pass

def get_subgraph(factid,student_id,path):
    with open(path,'r') as file:
        data=json.load(file)
        nodes=data['nodes']
        fact_nodes=[node for node in nodes if node['operation']=='fact']
        is_exist=False
        for fact_node in fact_nodes:
            if fact_node['factid']==factid:
                ## TODO 递归得到子图
        if not is_exist:
            return "subgraph does not exist",None