def init_node(nodes_ls):
    '''
    返回字典，key为节点的属性，值为对应的属性值
    '''
    nodes = {}
    for node in nodes_ls:
        nodes[node[0]] = node[1:] + [[]] # 为vertices创建空列表
    return nodes

def get_node_degree(edges):
    '''
    获取对应的节点度
    '''
    node_degree = {key: 0 for key in range(34282)}
    for edge in edges:
        node_degree[edge[0]] += 1
        node_degree[edge[1]] += 1
    return node_degree

def print_node(graph, ID):
    '''
    显示节点全部信息
    '''
    if ID == "all":
        for node in graph:
            how_to_print_node(node)
            print("\n")
    else:
        node = graph[ID]
        how_to_print_node(node, ID)

def how_to_print_node(node, ID):
    print("Node ID: {}\nNode Name: {}\nNode Weight: {}".format(ID, node[0], node[1]))
    print("Node Type: {}\nNode Info: {}".format(node[2], node[3]))
    print("Vertices: ")
    for ver in node[-1]:
        print("Node {} <-> Node {}".format(ID, ver))
