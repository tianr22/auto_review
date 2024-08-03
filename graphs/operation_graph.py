import json
import os
from pyvis.network import Network

# 获取当前文件夹下的所有文件
current_directory = os.getcwd()
json_files = os.listdir(current_directory)

# 创建一个新文件夹保存结果
result_directory = os.path.join(current_directory, 'result_storage')
os.makedirs(result_directory, exist_ok=True)

for json_file in json_files:
    if not json_file.endswith(".json"):
        continue

    with open(json_file, 'r') as file:
        print(json_file)

        # Convert the string into a JSON object
        data = json.load(file)
        
        nodes = data['nodes']

        # 创建网络图
        net = Network(height="960px", width="100%", bgcolor="#222222", font_color="white", notebook=True, directed=True)

        # 添加节点
        for node in nodes:
            if node['type'] == 'operation':
                from_contents = [n['content'] for n in nodes if n['id'] in node['from']]
                net.add_node(node['id'], label=node['content'], color='skyblue')

        # 添加边
        edges = set()  # 使用集合来避免重复的边
        for node in nodes:
            if node['type'] == 'operation':
                targets = node['to']
                for target in targets:
                    # 查找所有以target为from的节点
                    for other in nodes:
                        if target in other['from'] and other['type'] == 'operation':
                            
                            # 确保只添加一条边
                            if (node['id'], other['id']) not in edges and (other['id'], node['id']) not in edges:
                                
                                from_set = set(node['to'])
                                to_set = set(other['from'])

                                # 求交集
                                common = from_set & to_set
                                
                                net.add_edge(node['id'], other['id'], title=str(common))
                                edges.add((node['id'], other['id']))

        # 设置网络图的参数
        net.set_options("""
        var options = {
        "nodes": {
            "font": {
            "size": 16
            }
        },
        "edges": {
            "color": {
            "inherit": true
            },
            "smooth": false
        },
        "physics": {
                "enabled": true
            }
        }
        """)

        # 保存为HTML文件
        output_file = os.path.join(result_directory, json_file.split(".")[0] + '_operation.html')
        net.show(output_file)
