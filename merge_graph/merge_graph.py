import json
import os
import copy

class Merge_node:
    def __init__(self,fact=set(),contained_file=[]):
        self.fact = fact
        self.contained_file = contained_file
    
    def get_fact(self):
        return self.fact

class Graph:
    def __init__(self,start_node:Merge_node = None,end_node:Merge_node = None):
        self.nodes = []
        self.edges = []
        self.start_node = start_node
        self.end_node = end_node
        if start_node:
            self.add_node(start_node)
        if end_node:
            self.add_node(end_node)
        if start_node and end_node:
            self.add_edge((start_node,end_node))
    def add_node(self,node):
        self.nodes.append(node)
    def add_edge(self,edge):
        self.edges.append(edge)
    def remove_edge(self,edge):
        self.edges.remove(edge)

    def merge(self,graph):
        ## 将graph中的node和edge加入到self中
        self.remove_edge((graph.start_node,graph.end_node))
        for node in graph.nodes:
            if node == graph.start_node or node == graph.end_node:
                continue
            self.add_node(node)
        for edge in graph.edges:
            self.add_edge(edge)

    def display(self):
        print('nodes:')
        for node in self.nodes:
            print(node.get_fact())
        print('edges:')
        for edge in self.edges:
            print(edge[0].get_fact(),edge[1].get_fact())

def get_fact_id(student_fact,json_dic_path,json_file_path):
    with open(json_dic_path+json_file_path,'r') as file:
        data=json.load(file)
        nodes=data['nodes']
        for node in nodes:
            if node['id'] == student_fact:
                return node['factid']
        return None
    
def get_all_student_json_files(json_dic_path,ignore=False,student_status=None,ignore_status=None):
    json_files = os.listdir(json_dic_path)
    json_files=[json_file for json_file in json_files if json_file.endswith(".json") and json_file[0].isdigit()]
    json_files=sorted(json_files)
    if not ignore:
        return json_files
    if student_status is not None:
        json_files=[json_file for index,json_file in enumerate(json_files) if student_status[index] not in ignore_status]
        return json_files
    
# well tested
# 向前拓展得到子图
def get_subgraph_from_list(fact_out,op_nodes):
    contained_op_nodes = []
    while True:
        is_break = True
        for op_node in op_nodes:
            if op_node not in contained_op_nodes and any(fact in fact_out for fact in op_node['to']):
                contained_op_nodes.append(op_node)
                fact_out.extend(op_node['from'])
                fact_out = list(set(fact_out))
                is_break = False
        if is_break:
            break
    return set(fact_out),contained_op_nodes

# well tested
# 向后拓展得到子图
def get_subgraph_to_list(fact_in,op_nodes):
    contained_op_nodes = []
    while True:
        is_break = True
        for op_node in op_nodes:
            if op_node not in contained_op_nodes and all(fact in fact_in for fact in op_node['from']):
                contained_op_nodes.append(op_node)
                fact_in.extend(op_node['to'])
                fact_in = list(set(fact_in))
                is_break = False
        if is_break:
            break
    return set(fact_in),contained_op_nodes

def get_subgraph_tolist(fact_in,op_nodes):
    contained_op_nodes = []
    while True:
        is_break = True
        for op_node in op_nodes:
            if op_node not in contained_op_nodes and any(fact in fact_in for fact in op_node['from']):
                contained_op_nodes.append(op_node)
                fact_in.extend(op_node['to'])
                fact_in = list(set(fact_in))
                is_break = False
        if is_break:
            break
    return set(fact_in),contained_op_nodes

# well-tested(partly)
# 得到包含fact_in_list和fact_out_list的子图
def get_subgraph(fact_in_list,fact_out_list,json_dic_path,contained_file=None,initial=False,contained_op=None):
    if contained_file:
        json_files = contained_file
    else:
        json_files = get_all_student_json_files(json_dic_path)
    contained_fact = {} ##储存每个学生包含的fact_id
    _contained_op = {} ##储存每个学生包含的operation_id
    fact_id_cnt = {}
    for json_file in json_files:
        with open(json_dic_path+json_file,"r") as file:
            data = json.load(file) 
            nodes=data['nodes']
            op_nodes = [node for node in nodes if node['type']=='operation']
            fact_nodes = [node for node in nodes if node['type']=='fact']
            fact_id_list = list(set([fact_node['factid'] for fact_node in fact_nodes]))
            if all(fact_id in fact_id_list for fact_id in fact_in_list) and all(fact_id in fact_id_list for fact_id in fact_out_list):
                fact_in = [node['id'] for node in fact_nodes if node['factid'] in fact_in_list]
                fact_out = [node['id'] for node in fact_nodes if node['factid'] in fact_out_list]
                from_subgraph,cop_nodes1 = get_subgraph_from_list(fact_out,op_nodes)
                if initial:
                    to_subgraph,cop_nodes2 = get_subgraph_to_list(fact_in,op_nodes)
                else:
                    to_subgraph,cop_nodes2 = get_subgraph_tolist(fact_in,contained_op[json_file])   
                subgraph = from_subgraph.intersection(to_subgraph)
                cop_nodes = [cop_node for cop_node in cop_nodes1 if cop_node in cop_nodes2]
                subgraph = [get_fact_id(fact,json_dic_path,json_file) for fact in subgraph]
                subgraph = set(subgraph)
                if all(fact_id in subgraph for fact_id in fact_in_list) and all(fact_id in subgraph for fact_id in fact_out_list):
                    contained_fact[json_file] = subgraph
                    _contained_op[json_file] = cop_nodes
                    for factid in subgraph:
                        if factid in fact_in_list or factid in fact_out_list:
                            continue
                        if factid not in fact_id_cnt:
                            fact_id_cnt[factid] = 1
                        else:
                            fact_id_cnt[factid] += 1
    return contained_fact,fact_id_cnt,_contained_op

## 判断max-fact-pair的逻辑合理性
def judge_logic(fact_id_cnt,max_fact_id_list,contained_fact,json_dic_path,start_fact,end_fact):
    for fact_id in max_fact_id_list:
        # print('fact_id: ',fact_id)
        is_legal = True
        for json_file,_ in contained_fact.items():
            with open(json_dic_path+json_file,"r") as file:
                data = json.load(file)
                nodes = data['nodes']
                op_nodes = [node for node in nodes if node['type']=='operation']
                for op_node in op_nodes:
                    op_node['from'] = [get_fact_id(fact,json_dic_path,json_file) for fact in op_node['from']]
                    op_node['to'] = [get_fact_id(fact,json_dic_path,json_file) for fact in op_node['to']]
                    if any(fact in op_node['to'] for fact in start_fact) and any(fact in op_node['from'] for fact in fact_id):
                        print('here1')
                        is_legal = False
                        break
                    if any(fact in op_node['from'] for fact in end_fact) and any(fact in op_node['to'] for fact in fact_id):
                        print('here2')
                        is_legal = False
                        break
                if is_legal == False:
                    break
                for fact in set(fact_id_cnt.keys()).difference(fact_id):
                    # print('fact: ',fact)
                    if any(fact in op_node['to'] and any(_ in op_node['from'] for _ in fact_id) for op_node in op_nodes) and any(fact in op_node['from'] and any(_ in op_node['to'] for _ in fact_id) for op_node in op_nodes):
                        print('here3',fact)
                        is_legal = False
                        break
                if is_legal == False:
                    break
        if is_legal == True:
            return fact_id
    return None            
    


# well-tested(partly)
# 选择max_fact_pair
def select_max_fact_id(fact_id_cnt,contained_fact,start_node,end_node,json_dic_path):
    max_fact_id_list = []
    max_cnt = 0
    for _,cnt in fact_id_cnt.items():
        if cnt > max_cnt:
            max_cnt = cnt
    for fact_id,cnt in fact_id_cnt.items():
        if cnt == max_cnt:
            max_fact_id_list.append(fact_id)
    max_fact_id_list = [set([fact_id]) for fact_id in max_fact_id_list]
    identity_id_num = len(max_fact_id_list)
    ## 遍历max_fact_id_list中的所有组合，找到包含的fact最多的组合
    while True:
        is_continue = False
        _max_fact_id_list1 = copy.deepcopy(max_fact_id_list)
        for fact_id1 in _max_fact_id_list1[:identity_id_num]:
            for fact_id2 in _max_fact_id_list1:
                if fact_id1 == fact_id2 or fact_id1.issubset(fact_id2):
                    continue
                cnt = 0
                for _,fact_list in contained_fact.items():
                    if fact_id1.issubset(fact_list) and all(fact_id in fact_list for fact_id in fact_id2):
                        cnt += 1
                if cnt == max_cnt:
                    if fact_id1.union(fact_id2) not in max_fact_id_list:
                        max_fact_id_list.append(fact_id1.union(fact_id2))
                        is_continue = True
        if not is_continue:
            break
    max_fact_id_list = sorted(max_fact_id_list,key=lambda x:len(x),reverse=True)
    max_fact_id=judge_logic(fact_id_cnt,max_fact_id_list,contained_fact,json_dic_path,start_node,end_node)
    if max_fact_id is None:
        return None,None,None
    contained_file = []
    not_contained_file = []
    for json_file,fact_list in contained_fact.items():
        if all(fact_id in fact_list for fact_id in max_fact_id):
            contained_file.append(json_file)
        else:
            not_contained_file.append(json_file)
    return max_fact_id,contained_file,not_contained_file

# 初始化graph
def initial_graph(fact_in_list,fact_out_list,contained_fact):
    contained_file = list(contained_fact.keys())
    start_node = Merge_node(set(fact_in_list),contained_file)
    end_node = Merge_node(set(fact_out_list),contained_file)
    graph = Graph(start_node,end_node)
    return graph
    
# 从初始图得到完整图
def merge_graph(graph:Graph,contained_fact,fact_id_cnt,json_dic_path,contained_op):
    if fact_id_cnt == {}:
        return
    graph.remove_edge((graph.start_node,graph.end_node))
    not_contained_file = list(contained_fact.keys())
    while len(not_contained_file) > 0:
        contained_fact,fact_id_cnt,contained_op = get_subgraph(graph.start_node.get_fact(),graph.end_node.get_fact(),json_dic_path,not_contained_file,False,contained_op)
        max_fact_id,contained_file,not_contained_file= select_max_fact_id(fact_id_cnt,contained_fact,graph.start_node.get_fact(),graph.end_node.get_fact(),json_dic_path)   
        print('max_fact_id: ',max_fact_id)
        if max_fact_id is None and contained_file == None and not_contained_file == None:
            print('gggg')
            if (graph.start_node,graph.end_node) not in graph.edges:
                graph.add_edge((graph.start_node,graph.end_node))
            return
        print("not_contained_file: ",not_contained_file)
        print(max_fact_id)
        new_node = Merge_node(max_fact_id,contained_file)
        graph.add_node(new_node)
        graph.add_edge((graph.start_node,new_node))
        graph.add_edge((new_node,graph.end_node))
        print('xxxxx')
        graph.display()
        print('xxxxx')
        # 左侧
        left_contained_fact,left_fact_id_cnt,_contained_op = get_subgraph(graph.start_node.get_fact(),max_fact_id,json_dic_path,contained_file,contained_op=contained_op)
        print("left: ",left_contained_fact,left_fact_id_cnt)
        left_subgraph = Graph(graph.start_node,new_node)
        merge_graph(left_subgraph,left_contained_fact,left_fact_id_cnt,json_dic_path,_contained_op)
        graph.merge(left_subgraph)
        print('yyyyyyyyyy')
        graph.display()
        print('yyyyyyyyyy')
        ## 右侧
        print(max_fact_id,graph.end_node.get_fact())
        right_contained_fact,right_fact_id_cnt,_contained_op = get_subgraph(max_fact_id,graph.end_node.get_fact(),json_dic_path,contained_file,contained_op=contained_op)
        print("right: ",right_contained_fact,right_fact_id_cnt)
        right_subgraph = Graph(new_node,graph.end_node)
        merge_graph(right_subgraph,right_contained_fact,right_fact_id_cnt,json_dic_path,_contained_op)
        graph.merge(right_subgraph)
        print('zzzzzzzz')
        graph.display()
        print('zzzzzzzz')
    return

# 得到最终的结果图
def get_final_graph(fact_in_list,fact_out_list,json_dic_path):
    contained_fact,fact_id_cnt,contained_op = get_subgraph(fact_in_list,fact_out_list,json_dic_path,initial=True)
    print(contained_op['1.txt.json'])
    if contained_fact == {}:
        return None
    graph = initial_graph(fact_in_list,fact_out_list,contained_fact)
    # print('initial graph')
    # graph.display()
    merge_graph(graph,contained_fact,fact_id_cnt,json_dic_path,contained_op)
    return graph

if __name__ == "__main__":
    ## 进行一些测试
    json_dic_path = "/home/user/shared/solving_data/student_graph3/"
    # json_file_path = '/home/user/shared/solving_data/student_graph3/1.txt.json'
    # with open(json_file_path,"r") as file:
    #     data = json.load(file)
    #     nodes = data['nodes']
    #     op_nodes = [node for node in nodes if node['type']=='operation']
    # fact_in = [1,2]
    # fact_out = [11]
    # fact_out_list,_ = get_subgraph_from_list(fact_out,op_nodes)
    # fact_in_list,_ = get_subgraph_to_list(fact_in,op_nodes)
    fact_in_id = [1,2]
    fact_out_id = [9]
    # print(fact_out_list)
    # print(fact_in_list)
    # contained_fact,fact_id_cnt = get_subgraph(fact_in_id,fact_out_id,json_dic_path)
    # print(contained_fact)
    # print(fact_id_cnt)
    # max_fact_id,contained_file,not_contained_file = select_max_fact_id(fact_id_cnt,contained_fact)
    # print(max_fact_id)
    # print(contained_file)
    # print(not_contained_file)
    graph = get_final_graph(fact_in_id,fact_out_id,json_dic_path)
    if graph:
        print('final graph')
        graph.display()
    else:
        print('no graph')