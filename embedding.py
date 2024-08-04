## TODO 解决import问题


import networkx as nx
from node2vec import Node2Vec
# 创建一个空的有向图
G = nx.DiGraph()

# 添加节点
facts = [1, 2, 3]
conclusions = [4, 5]

for fact in facts:
    G.add_node(fact, label=f"Fact {fact}")

for conclusion in conclusions:
    G.add_node(conclusion, label=f"Conclusion {conclusion}")

G.add_edge(1, 4)
G.add_edge(2, 4)

# Fact 3 和 Conclusion 4 导出 Conclusion 5
G.add_edge(3, 5)
G.add_edge(4, 5)

node2vec = Node2Vec(G, dimensions=64, walk_length=30, num_walks=200, workers=4)
model = node2vec.fit(window=10, min_count=1, batch_words=4)
# model.wv.save_word2vec_format("embedding.emb")
print(model.wv['1'])