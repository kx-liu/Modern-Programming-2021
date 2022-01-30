from GraphStat.NetworkBuilder import graph
from GraphStat.NetworkBuilder import node
from GraphStat.NetworkBuilder import stat
from GraphStat.Visualization  import plotgraph
from GraphStat.Visualization  import plotnodes

def read_file():
    nnodes = 34282
    nodes_ls = []
    edges_ls = []
    with open("newmovies.txt", encoding="utf-8") as f:
        for i in range(nnodes + 2):
            temp = f.readline().strip("\n").split("\t")
            if i == 0: continue # 略去第一行
            temp[1] = eval(temp[1]); temp[0] = int(temp[0])
            nodes_ls.append(temp)
        temp = f.readline()
        while True:
            temp = f.readline()
            if len(temp) == 0: break
            temp_ls = temp.strip("\n").split("\t")
            temp_ls[0] = int(temp_ls[0]); temp_ls[1] = int(temp_ls[1]); temp_ls.pop()
            temp_tup = tuple(sorted(temp_ls))
            edges_ls.append(temp_tup)
    edges = list(set(edges_ls))
    return nodes_ls, edges

def main():
    nodes_ls, edges = read_file()
    nodes = node.init_node(nodes_ls) # ; print(nodes[1])
        # return : {0: [feat0, []], 1: [feat1, []], ...}
    graphs = graph.init_graph(nodes, edges) # ; print(graphs[1])
        # return : {0: [feat0, [conn0]], 1: [feat1, [conn1]], ...}
    node_degree = node.get_node_degree(edges) # ; print(node_degree[1])
        # return : {0: degree0, 1: degree1, ...}
    # node.print_node(graphs, ID=1)
    n = stat.cal_average_degree(graphs) # ; print(n)
    degree_dis = stat.cal_degree_distribution(graphs) # ; print(degree_dis)
        # return : {0: n0, 1: n1, ...}, key for degree and value for its frequency
    # graph.save_graph(graphs)
    # graph = graph.load_graph("graph.xlsx")
    # plotnodes.plot_nodes_attr(graphs, feature="Age")
    plotgraph.plot_degree_distribution(degree_dis)

if __name__ == "__main__":
    main()