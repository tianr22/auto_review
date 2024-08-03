import pandas as pd
import os
import json
import numpy as np
import ast

def select_student():
    ## 选择下一个进行批改的学生
    pass

def get_all_student_json_files(json_dic_path,ignore=False,student_status=None):
    json_files = os.listdir(json_dic_path)
    json_files=sorted(json_files)
    json_files=[json_file for json_file in json_files if json_file[0].endswith(".json") and json_file[0].isdigit()]
    if not ignore:
        return json_files
    if student_status is not None:
        json_files=[json_file for index,json_file in enumerate(json_files) if student_status[index]!='A']
        return json_files

## 读取judge info
def read_info(store_path,same_in_df_right_path,from_student_id_list_path):
    with open(store_path, 'r') as f:
        store_dict = json.load(f)
    with open(same_in_df_right_path) as f:
        data_same_in = pd.read_csv(f)
    from_student_id_list = np.load(from_student_id_list_path)
    return store_dict,data_same_in,from_student_id_list

## 前端发送批改好的学生数据给后端。后端更新学生数据
def refresh_student_data(review_id,update_data):
    # TODO backend Update student_data
    ## 更新student_left_id
    student_left_id=[i for i in student_left_id if i != review_id]
    pass

def refresh_backend_data(json_dic_path,store_path,same_in_df_right_path,from_student_id_list_path):
    # 通过fact更新所有的operation的正误
    # 原则是如果输入都对，但是输出包含错误信息，则op错
    # 如果输出都对，输入包含错误信息，则op错
    # 但是如果输入输出都包含错误，则无法判断，需要老师进行矫正
    store_dict,data_same_in,from_student_id_list=read_info(store_path,same_in_df_right_path,from_student_id_list_path)
    fact_info=store_dict['pair_info']
    operation_right=store_dict['operation_right']
    operation_wrong=store_dict['operation_wrong']
    pair_info=store_dict['pair_info']
    student_op_num=store_dict['student_op_num']
    num_student=store_dict['student_num']
    student_status=store_dict['student_status']
    operation_status=store_dict['operation_status']
    json_files=get_all_student_json_files(json_dic_path)
    student_to_delete=[]
    ## use fact info to refresh op
    for id,status,json_file in zip(enumerate(student_status),json_files):
        ## 如果该学生已被老师批改
        if status == 'A':
            continue
        ## 每次都需要重新检验未批完的学生的op
        student_status[id]='C'
        operation_wrong[id]=[]
        operation_right[id]=[]
        operation_status[id]=["C" for _ in range(student_op_num[id])]
        with open(json_dic_path+json_file, 'r') as file:
            data=json.load(file)
            nodes=data["nodes"]
            op_nodes=[node for node in nodes if node['type']=='operation']
            for index,op_node in enumerate(op_nodes):
                is_from_correct=True
                is_to_correct=True
                is_from_uncertain=False
                is_to_uncertain=False
                for from_node_id in op_node['from']:
                    from_node=[_ for _ in nodes if _["id"]==from_node_id][0]
                    if fact_info[from_node["factid"]-1]==0:
                        is_from_correct = False
                        break
                    elif fact_info[from_node["factid"]-1]==-1:
                        is_from_uncertain=True
                for to_node_id in op_node['to']:
                    to_node=[_ for _ in nodes if _["id"]==to_node_id][0]
                    if fact_info[to_node["factid"]-1]==0:
                        is_from_correct = False
                        break
                    elif fact_info[to_node["factid"]-1]==-1:
                        is_to_uncertain=True
                if is_from_uncertain or is_to_uncertain:
                    if is_from_correct == is_to_correct:
                        pass
                    elif (is_from_correct and not is_from_uncertain) or (is_to_correct and not is_to_uncertain):
                        operation_wrong[id].append(op_node['id'])
                        operation_status[id][index]='B'
                    else: 
                        pass
                elif is_from_correct and is_to_correct:
                    operation_right[id].append(op_node['id'])
                    operation_status[id][index]='B'
                elif is_from_correct != is_to_correct:
                    operation_wrong[id].append(op_node['id'])
                    operation_status[id][index]='B'
                if all(_=='B' for _ in operation_status[id]):
                    student_status[id]='B'
                                             
    # 根据现在的operation的正误，更新pair的正误
    while True:
        is_need_continue=False
        for pair_id in range(len(data_same_in)):
            pair_info[pair_id]=-1
            def refresh_pair(from_student_id):
                consist_ops = data_same_in.loc[pair_id, str(from_student_id + 1)]
                if consist_ops=="set()":
                    continue
                else:
                    consist_ops = ast.literal_eval(data_same_in.loc[pair_id, str(from_student_id + 1)])
                is_pair_correct=True
                is_pair_unknown=False
                for opeation_id in consist_ops:
                    if opeation_id not in operation_right[pair_id]:
                        if opeation_id in operation_wrong[pair_id]:
                            is_pair_correct=False
                            is_pair_unknown=False
                            break
                        else:
                            is_pair_unknown=True
                return is_pair_correct,is_pair_unknown
            for student_id in range(num_student):
                is_pair_correct,is_pair_unknown=refresh_pair(student_id)
                # 只要有能判断pair正确的，这个pair就是正确的
                if is_pair_correct:
                    pair_info[pair_id]=1
                    break
                elif is_pair_unknown:
                    pair_info[pair_id]=-1
                    
            in_data = ast.literal_eval(data_same_in.loc[pair_id,"in"])
            out_data = ast.literal_eval(data_same_in.loc[pair_id,"out"])
            student_to_delete=[]
            for index,json_file in zip(student_left_id,json_files):
                with open(json_dic_path+json_file,'r') as file:
                    data=json.load(file)
                    nodes=data['nodes']
                    op_nodes=[node for node in nodes if node['type']=='operation']
                    for op_node in op_nodes:
                        if op_node['id'] in operation_right[index] or op_node['id'] in operation_wrong[index]:
                            continue
                        from_fact_set=set([node['factid'] for node in nodes if node['id'] in op_node['from']])
                        to_fact_set=set([node['factid'] for node in nodes if node['id'] in op_node['to']])
                        if from_fact_set==in_data:
                            if pair_info[pair_id] and to_fact_set.issubset(out_data):
                                operation_right[index].append(op_node['id'])
                                is_need_continue=True
                            elif pair_info[pair_id]==0 and out_data.issubset(to_fact_set):
                                operation_wrong[index].append(op_node['id'])
                                is_need_continue=True
                if len(operation_wrong[index])+len(operation_right[index])==student_op_num[index]:
                    student_to_delete.append(index)
            if len(student_to_delete) > 0:
                student_left_id=[i for i in student_left_id if i not in student_to_delete]
                json_files=get_all_student_json_files(json_dic_path,student_left_id)
                if len(student_left_id)==0:
                    is_need_continue=False
                    break
        if not is_need_continue:
            break
    store_dict['operation_right']=operation_right
    store_dict['operation_wrong']=operation_wrong
    store_dict['student_left_id']=student_left_id
    store_dict['pair_info']=pair_info
    with open(store_path, 'w') as f:
        json.dump(store_dict, f, indent=4)

def is_finished(store_path):
    with open(store_path, 'r') as f:
        store_dict = json.load(f)
    student_left_id=store_dict['student_left_id']
    if len(student_left_id)==0:
        return True
    else:
        return False

## init_auto_judge
def judge_init(json_dic_path,store_path,fact_list_path,same_in_df_right_path):
    ## 配置相关参数
    with open(fact_list_path, 'r', encoding='utf-8') as file:
        # 读取文件的所有内容
        list_str = file.read()
        # 将字符串解析为列表
        fact_list = json.loads(list_str)
    fact_list_length=len(fact_list)
    # 记录所有 fact 的正误，1代表正确，0代表错误,-1代表未知
    fact_info=[-1 for _ in range(fact_list_length)]
    # 记录每个人当前operation的状态
    operation_status={}
    operation_right={}
    operation_wrong={}
    json_files=get_all_student_json_files(json_dic_path)
    with open(same_in_df_right_path) as f:
        data_same_in = pd.read_csv(f)
    ## 表示pair的正误,-1表示未知
    pair_info = [-1 for i in range(len(data_same_in))]
    # 学生数量
    num_student=len(json_files)
    # 学生共有两种状态，老师手动批改过的学生为A，自动推断批完的学生为B，其余为C
    student_status=['C' for _ in range(num_student)]
    student_op_num=[]
    for index,json_file in enumerate(json_files):
        operation_right[index]=[]
        operation_wrong[index]=[] 
        student_data=json.load(json_file)
        student_nodes=student_data['nodes']
        student_op_nodes=[op_node for op_node in student_nodes if op_node['type']=='operation']
        student_op_num.append(len(student_op_nodes))
        # C表示unknown B代表推断 A代表老师批改
        operation_status[index]=['C' for _ in range(len(student_op_nodes))]   
    student_left_id=[i for i in range(num_student)]
    store_dict={}
    store_dict['operation_right']=operation_right
    store_dict['operation_wrong']=operation_wrong
    store_dict['student_num']=num_student
    store_dict['fact_info']=fact_info
    store_dict['student_op_num']=student_op_num
    store_dict['student_left_id']=student_left_id
    store_dict['pair_info']=pair_info
    store_dict['student_status']=student_status
    store_dict['operation_status']=operation_status
    with open(store_path, 'w') as f:
        json.dump(store_dict, f, indent=4)

def auto_judge(review_id,update_data,json_dic_path,store_path,same_in_df_right_path,from_student_id_list_path):
    ## review_id为批改学生id
    ## 根据一次学生作业数据自动批改，返回下一个批改的学生
    refresh_student_data(review_id,update_data)
    refresh_backend_data(json_dic_path,store_path,same_in_df_right_path,from_student_id_list_path)
    if is_finished(store_path):
        return "Already finish"
    else:
        return select_student()