import pandas as pd
import os
import json
import ast
class Info:
    def __init__(self,**kwargs):
        self.student_fact_status = kwargs.get('student_fact_status', {} )
        self.operation_right = kwargs.get('operation_right', {} )
        self.operation_wrong = kwargs.get('operation_wrong', {} )
        self.student_num = kwargs.get('student_num', 0 )
        self.fact_info = kwargs.get('fact_info', [] )
        self.student_op_num = kwargs.get('student_op_num', [] )
        self.student_fact_num = kwargs.get('student_fact_num', [] )
        self.pair_info = kwargs.get('pair_info', [] )
        self.student_status = kwargs.get('student_status', [] )
        self.operation_status = kwargs.get('operation_status', {} )

    def update(self, **kwargs):
        self.student_fact_status = kwargs.get('student_fact_status', self.student_fact_status)
        self.operation_right = kwargs.get('operation_right', self.operation_right)
        self.operation_wrong = kwargs.get('operation_wrong', self.operation_wrong)
        self.student_num = kwargs.get('student_num', self.student_num)
        self.fact_info = kwargs.get('fact_info', self.fact_info)
        self.student_op_num = kwargs.get('student_op_num', self.student_op_num)
        self.student_fact_num = kwargs.get('student_fact_num', self.student_fact_num)
        self.pair_info = kwargs.get('pair_info', self.pair_info)
        self.student_status = kwargs.get('student_status', self.student_status)
        self.operation_status = kwargs.get('operation_status', self.operation_status)

    def save_as_json(self, path):
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    @classmethod
    def load_from_json(cls, path):
        with open(path, 'r') as f:
            dic = json.load(f)
        obj = cls()
        obj.__dict__.update(dic)
        return obj

## DONE
def get_all_student_json_files(json_dic_path,ignore=False,student_status=None):
    json_files = os.listdir(json_dic_path)
    json_files=[json_file for json_file in json_files if json_file.endswith(".json") and json_file[0].isdigit()]
    json_files=sorted(json_files)
    if not ignore:
        return json_files
    if student_status is not None:
        json_files=[json_file for index,json_file in enumerate(json_files) if student_status[index]!='A']
        return json_files

## TODO  
def select_student():
    ## 选择下一个进行批改的学生
    pass

## DONE
## 读取judge info
def read_info(store_path,same_in_df_right_path):
    info = Info.load_from_json(store_path)
    with open(same_in_df_right_path) as f:
        data_same_in = pd.read_csv(f)
    return info,data_same_in

## 前端发送批改好的学生数据给后端。后端更新学生数据
def refresh_student_data(review_id,update_data):
    # TODO backend Update student_data
    pass

## DONE
## TO BE CHECKED
def refresh_backend_data(json_dic_path,store_path,same_in_df_right_path):
    # 通过fact更新所有的operation的正误
    # 原则是如果输入都对，但是输出包含错误信息，则op错
    # 如果输出都对，输入包含错误信息，则op错
    # 但是如果输入输出都包含错误，则无法判断，需要老师进行矫正
    info,data_same_in=read_info(store_path,same_in_df_right_path)
    student_fact_status=info.student_fact_status
    fact_info=info.fact_info
    operation_right=info.operation_right
    operation_wrong=info.operation_wrong
    pair_info=info.pair_info
    student_op_num=info.student_op_num
    student_fact_num=info.student_fact_num
    num_student=info.student_num
    student_status=info.student_status
    operation_status=info.operation_status
    json_files=get_all_student_json_files(json_dic_path)
    ## use fact info to refresh op
    for id,status,json_file in zip(enumerate(student_status),json_files):
        ## 如果该学生已被老师批改
        if status == 'A':
            continue
        ## 更新未经老师批改的学生的状态
        ## 每次都需要重新检验未批完的学生的op
        student_status[id]='C'
        operation_wrong[id]=[]
        operation_right[id]=[]
        operation_status[id]=["C" for _ in range(student_op_num[id])]
        student_fact_status[id]=['unknown' for _ in range(student_fact_num[id])]
        with open(json_dic_path+json_file, 'r') as file:
            data=json.load(file)
            nodes=data["nodes"]
            op_nodes=[node for node in nodes if node['type']=='operation']
            fact_nodes=[node for node in nodes if node['type']=='fact']
            # 更新学生fact状态
            for index,fact_node in enumerate(fact_nodes):
                if fact_info[fact_node['factid']-1]!=-1:
                    student_fact_status[id][index]='known'
            # 更新op状态
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
                        ## 更新op状态
                        operation_status[id][index]='B_fact'
                    else: 
                        pass
                elif is_from_correct and is_to_correct:
                    operation_right[id].append(op_node['id'])
                    operation_status[id][index]='B_fact'
                elif is_from_correct != is_to_correct:
                    operation_wrong[id].append(op_node['id'])
                    operation_status[id][index]='B_fact'
                if all(_=='B_fact' for _ in operation_status[id]):
                    student_status[id]='B'
                                             
    # 根据现在的operation的正误，更新pair的正误
    while True:
        ## 更新pair
        for pair_id in range(len(data_same_in)):
            pair_info[pair_id]=-1
            def refresh_pair(from_student_id):
                consist_ops = data_same_in.loc[pair_id, str(from_student_id + 1)]
                is_exist=True
                is_pair_correct=True
                is_pair_unknown=False
                if consist_ops=="set()":
                    is_exist=False
                    return is_pair_correct,is_pair_unknown,is_exist
                else:
                    consist_ops = ast.literal_eval(data_same_in.loc[pair_id, str(from_student_id + 1)])
                for opeation_id in consist_ops:
                    if opeation_id not in operation_right[pair_id]:
                        if opeation_id in operation_wrong[pair_id]:
                            is_pair_correct=False
                            is_pair_unknown=False
                            break
                        else:
                            is_pair_unknown=True
                return is_pair_correct,is_pair_unknown,is_exist
            if any(is_exist and is_pair_correct and not is_pair_unknown for is_pair_correct,is_pair_unknown,is_exist in [refresh_pair(student_id) for student_id in range(num_student)]):
                pair_info[pair_id]=1
            elif all(not is_exist or not is_pair_correct for is_pair_correct,_,is_exist in [refresh_pair(student_id) for student_id in range(num_student)]):
                pair_info[pair_id]=0
        ## 完成pair的更新  

        ## 检查是否有op更新  
        is_need_continue=False
        for pair_id in range(len(data_same_in)):
            in_data = ast.literal_eval(data_same_in.loc[pair_id,"in"])
            out_data = ast.literal_eval(data_same_in.loc[pair_id,"out"])
            for id,status,json_file in zip(enumerate(student_status),json_files):
                if status!="C":
                    continue
                with open(json_dic_path+json_file,'r') as file:
                    data=json.load(file)
                    nodes=data['nodes']
                    op_nodes=[node for node in nodes if node['type']=='operation']
                    for index,op_node in enumerate(op_nodes):
                        if operation_status[id][index]!='C':
                            continue
                        from_fact_set=set([node['factid'] for node in nodes if node['id'] in op_node['from']])
                        to_fact_set=set([node['factid'] for node in nodes if node['id'] in op_node['to']])
                        if from_fact_set==in_data:
                            if pair_info[pair_id] and to_fact_set.issubset(out_data):
                                operation_right[index].append(op_node['id'])
                                operation_status[id][index]='B_pair'
                                is_need_continue=True
                            elif pair_info[pair_id]==0 and out_data.issubset(to_fact_set):
                                operation_wrong[index].append(op_node['id'])
                                operation_status[id][index]='B_pair'
                                is_need_continue=True
                if all(_!='C' for _ in operation_status[id]):
                    student_status[id]='B'
        if not is_need_continue:
            break
    info.update(student_fact_status=student_fact_status,
                operation_right=operation_right,
                operation_wrong=operation_wrong,
                pair_info=pair_info,
                student_status=student_status,
                operation_status=operation_status
                )
    info.save_as_json(store_path)

## DONE
def is_finished(store_path):
    info = Info.load_from_json(store_path)
    if all(_!='C' for _ in info.student_status):
        return True
    return False

## DONE 
## init_auto_judge
def judge_init(json_dic_path,store_path,fact_list_path,same_in_df_right_path):
    ## 配置相关参数
    with open(fact_list_path, 'r', encoding='utf-8') as file:
        # 读取文件的所有内容
        list_str = file.read()
        # 计算 "factid" 出现的次数
        fact_list_length = list_str.count('"factid"')
    # 记录所有 fact 的正误，1代表正确，0代表错误,-1代表未知
    fact_info=[-1 for _ in range(fact_list_length)]
    # 记录每个人当前operation的状态
    operation_status={}
    operation_right={}
    operation_wrong={}
    student_fact_status={}
    with open(same_in_df_right_path) as f:
        data_same_in = pd.read_csv(f)
    ## 表示pair的正误,-1表示未知
    pair_info = [-1 for _ in range(len(data_same_in))]
    json_files=get_all_student_json_files(json_dic_path)
    # 学生数量
    num_student=len(json_files)
    # 学生共有两种状态，老师手动批改过的学生为A，自动推断批完的学生为B，其余为C
    # Update
    student_status=['C' for _ in range(num_student)]
    student_op_num=[]
    student_fact_num=[]
    for index,json_file in enumerate(json_files):
        operation_right[index]=[]
        operation_wrong[index]=[] 
        with open(json_dic_path+json_file, 'r') as json_file:
            student_data=json.load(json_file)
            student_nodes=student_data['nodes']
            student_fact_nodes=[fact_node for fact_node in student_nodes if fact_node['type']=='fact']
            student_op_nodes=[op_node for op_node in student_nodes if op_node['type']=='operation']
            student_op_num.append(len(student_op_nodes))
            student_fact_num.append(len(student_fact_nodes))
            # C表示unknown B代表推断 A代表老师批改
            # Update: B分为两种 B_fact 表示由fact推断，B_pair 表示由pair推断出来的结果
            # 优先级：A > B_fact > B_pair > C
            operation_status[index]=['C' for _ in range(len(student_op_nodes))]
            # fact_status 共有两种 known/unknown
            student_fact_status[index]=['unknown' for _ in range(len(student_fact_nodes))]   
    info=Info(student_fact_status=student_fact_status,
              operation_right=operation_right,
              operation_wrong=operation_wrong,
              student_num=num_student,
              fact_info=fact_info,
              student_op_num=student_op_num,
              student_fact_num=student_fact_num,
              pair_info=pair_info,
              student_status=student_status,
              operation_status=operation_status
              )
    info.save_as_json(store_path)

## DONE
def auto_judge(review_id,update_data,json_dic_path,store_path,same_in_df_right_path):
    ## review_id为批改学生id
    ## 根据一次学生作业数据自动批改，返回下一个批改的学生
    refresh_student_data(review_id,update_data)
    refresh_backend_data(json_dic_path,store_path,same_in_df_right_path)
    if is_finished(store_path):
        return "Already finish"
    else:
        return select_student()

if __name__ == "__main__":
    json_dic_path = '/home/user/shared/solving_data/student_graph3/'
    store_path = 'store.json'
    fact_list_path = '/home/user/shared/solving_data/student_graph3/facts_list_v4.txt'
    same_in_df_right_path = 'data/same_in_df_right.csv'
    judge_init(json_dic_path,store_path,fact_list_path,same_in_df_right_path)
    