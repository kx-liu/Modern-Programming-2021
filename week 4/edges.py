import pandas as pd

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

def csv_file(nodes_ls, edges):
    edges.sort(key=lambda x:x[0])
    edges_ls = []
    for i in range(len(edges)):
        edge = [edges[i][0], edges[i][1]]
        edge.append("undirected")
        edge.append(nodes_ls[edges[i][0]][1])
        edges_ls.append(edge)
    df = pd.DataFrame(edges_ls)
    df.columns = ["Source", "Target", "Type", "Name"]
    print(df.head())
    df.to_csv("edges.csv")
    
def main():
    nodes_ls, edges = read_file()
    csv_file(nodes_ls, edges)

if __name__ == '__main__':
    main()