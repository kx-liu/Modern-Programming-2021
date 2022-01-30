import pandas as pd

def init_graph(nodes, edges):
    '''
    返回一个字典，分别存储节点信息和边信息
    '''
    for edge in edges:
        nodes[edge[0]][-1].append(edge[1])
        nodes[edge[1]][-1].append(edge[0])
    return nodes

def save_graph(graph):
    '''
    序列化图信息
    '''
    index = []
    data = []
    for item in graph.items():
        index.append(item[0])
        data.append(item[1])
    columns = ["Name", "Weight", "Type", "Info", "vertices"]
    df = pd.DataFrame(data, columns=columns, index=index)
    df.to_excel("graph.xlsx")

def load_graph(addr):
    '''
    显示图全部信息
    '''
    df = pd.read_excel(addr)
    graph = {}
    for i in range(df.shape[0]):
        graph[i] = df.loc[i].tolist()[1:]
    return graph
