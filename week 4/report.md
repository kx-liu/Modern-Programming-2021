## 第四次作业 自建包——图的处理

### 4.1 包结构展示

- GraphStat/

  \__init__.py

  - NetworkBuilder/
    - \__init__.py
    - node.py
    - stat.py
    - graph.py
  - Visualization/
    - \__init__.py
    - plotgraph.py
    - plotnodes.py

<img src="https://s2.loli.net/2022/01/29/VBLlEC6TvgunAFy.png" alt="image-20211022211416941" style="zoom:50%;" />

### 4.2 GraphStat

```python
# __init__.py
'''
实现相关网络的构建和可视化的包

@author: Liu_K_X
'''
import sys; sys.path.append("D:\\vscode py\\现代程设\\week 4")
__all__ = ["graph", "node", "stat", "plotgraph", "plotnodes"]
```

### 4.3 GraphStat.NetworkBuilder

#### 4.3.0 GraphStat.NetworkBuilder.\__init__

```python
# __init__.py
'''
用以实现点和图结构的创建，以及相关的基础统计功能
'''
import GraphStat.NetworkBuilder.graph
import GraphStat.NetworkBuilder.node
import GraphStat.NetworkBuilder.stat
__all__ = ["graph", "node", "stat"]
```

- 子包的\__init__.py文件中需要包含import语句，以导入子包下的module。

#### 4.3.1 GraphStat.NetworkBuilder.node

```python
# node.py
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
        how_to_print_node(node)

def how_to_print_node(node):
    print("Node ID: {}\nNode Name: {}\nNode Weight: {}".format(node[0], node[1], node[2]))
    print("Node Type: {}\nNode Info: {}".format(node[3], node[4]))
    for ver in node[-1]:
        print("Node {} --> Node {}".format(node[0], ver))
```

- 函数`init_node(nodes_ls)`：返回字典，节点ID为key，其余属性外加一个空列表（为储存其连接的节点ID）为value，结构如下：`{0: [feat0, []], 1: [feat1, []], ...}`；

- 函数`get_node_degree(edges)`：返回字典，节点ID为key，对应的度为value，结构如下：`{0: degree0, 1: degree1, ...}`；
- 函数`print_node(graph, ID)`：调用`how_to_print_node(node)`打印ID节点的属性。

#### 4.3.2 GraphStat.NetworkBuilder.graph

```python
# graph.py
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
    columns = ["Name", "Weight", "Type", "Info", "Vertices"]
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
```

- 函数`init_graph(nodes, edges)`：返回字典，节点ID为key，其余属性为value，结构如下：`{0: [feat0, [conn0]], 1: [feat1, [conn1]], ...}`；
- 函数`save_graph(graph)`：生成xlsx文件以储存各节点信息；
- 函数`load_graph(addr)`：读取xlsx文件，返回graph。

#### 4.3.3 GraphStat.NetworkBuilder.stat

```python
# stat.py
def cal_average_degree(graph):
    '''
    计算网络中的平均度
    '''
    a = 0
    b = 0
    for value in graph.items():
        a += len(value[1][-1])
        b += 1
    return a / b

def cal_degree_distribution(graph):
    '''
    计算网络的度分布
    '''
    degree_dic = {key: 0 for key in range(1500)}
    for item in graph.items():
        degree = len(item[1][-1])
        degree_dic[degree] += 1
    
    return degree_dic
```

- 函数`cal_average_degree(graph)`：计算整个网络的平均度，返回float；
- 函数`cal_degree_distribution(graph)`：返回字典，度为key，对应频数为value。

### 4.4 GraphStat.Visualization

#### 4.4.0 GraphStat.Visualization.\__init__

```python
# __init__.py
'''
基于NetworkBuilder构建的图和节点结构，
利用matplotlib等绘制相关的统计结果
'''
import GraphStat.Visualization.plotgraph
import GraphStat.Visualization.plotnodes
__all__ = ["plotgraph", "plotnodes"]
```

#### 4.4.1 GraphStat.Visualization.plotgraph

```python
# plotgraph.py
import matplotlib.pyplot as plt

def plot_degree_distribution(degree_dis):
    '''
    度的分布图
    '''
    x = []
    y = []
    for item in degree_dis.items():
        x.append(item[0])
        y.append(item[1])
    plt.plot(x[:100], y[:100])
    plt.xlabel("frequency"); plt.ylabel("degree")
    plt.title("Nodes Distribution")
    plt.show()
```

- 绘制度的分布图。

#### 4.4.2 GraphStat.Visualization.plotnodes

```python
# plotnodes.py
import re
import matplotlib.pyplot as plt

def plot_nodes_attr(graph, feature):
    '''
    绘制图中节点属性的统计结果
    '''
    if feature == "Type":
        type_dic = {'writer': 0, 'movie': 0, 'director':0 , 'starring':0}
        for item in graph.items():
            type_dic[item[1][2]] += 1
        plt.bar(list(type_dic.keys()), list(type_dic.values()))
        plt.title("Type's Distribution")
        plt.xlabel("type"); plt.ylabel("frequency")
        plt.show()
    if feature == "Birth":
        birth_ls = [0] * 12
        for item in graph.items():
            feat = item[1][-2]
            birth = re.search("(BC\s)*[0-9]+\sbirths", feat)
            if birth == None: continue
            else:
                if "BC" in birth.group():
                    birth = 0 - int(re.search("[0-9]+", birth.group()).group())
                else:
                    birth = int(re.search("[0-9]+", birth.group()).group())
                if birth < 1900: birth_ls[0] += 1
                elif birth >= 2000: birth_ls[-1] += 1
                else: birth_ls[(birth - 1900) // 10 + 1] += 1
        x = ["<1900", "[1900, 1910)", "[1910, 1920)", "[1920, 1930)", "[1930, 1940)", 
             "[1940, 1950)", "[1950, 1960)", "[1960, 1970)", "[1970, 1980)", "[1980, 1990)", 
             "[1990, 2000)", ">=2000"]
        plt.bar(x, birth_ls)
        plt.title("Birth's Distribution")
        plt.xlabel("birth year"); plt.ylabel("frequency")
        plt.xticks(rotation=30)
        plt.show()
    if feature == "Age":
        age_ls = [0] * 11
        for item in graph.items():
            feat = item[1][-2]
            birth = re.search("(BC\s)*[0-9]+\sbirths", feat)
            death = re.search("(BC\s)*[0-9]+\sdeaths", feat)
            if birth == None or death == None: continue
            else:
                if "BC" in birth.group():
                    birth = 0 - int(re.search("[0-9]+", birth.group()).group())
                else:
                    birth = int(re.search("[0-9]+", birth.group()).group())
                if "BC" in death.group():
                    death = 0 - int(re.search("[0-9]+", death.group()).group())
                else:
                    death = int(re.search("[0-9]+", death.group()).group())
                age = death - birth
                age_ls[age // 10] += 1
        x = ["[0, 10)", "[10, 20)", "[20, 30)", "[30, 40)", "[40, 50)", "[50, 60)", 
             "[60, 70)",  "[70, 80)", "[80, 90)", "[90, 100)", ">=100"]
        plt.bar(x, age_ls)
        plt.title("Age's Distribution")
        plt.xlabel("age"); plt.ylabel("frequency")
        plt.xticks(rotation=30)
        plt.show()
```

- `feature == "Type"`：统计各节点类型的人数，绘制直方图；
- `feature == "Birth"`：统计各节点出生年份的分布，发现有公元前数据，需做特殊处理，绘制直方图；
- `feature == "Age"`：统计各节点的年龄，绘制直方图。

### 4.5 主文件代码

```python
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
    edges = list(set(edges_ls)) # 去重
    return nodes_ls, edges

def main():
    nodes_ls, edges = read_file()
    nodes = node.init_node(nodes_ls) ; print(nodes[1])
        # return : {0: [feat0, []], 1: [feat1, []], ...}
    graphs = graph.init_graph(nodes, edges) # ; print(graphs[1])
        # return : {0: [feat0, [conn0]], 1: [feat1, [conn1]], ...}
    node_degree = node.get_node_degree(edges) # ; print(node_degree[1])
        # return : {0: degree0, 1: degree1, ...}
    node.print_node(graphs, ID=1)
    n = stat.cal_average_degree(graphs) # ; print(n)
    degree_dis = stat.cal_degree_distribution(graphs)
        # return : {0: n0, 1: n1, ...}, key for degree and value for its frequency
    graph.save_graph(graphs)
    graph = graph.load_graph("graph.xlsx")
    plotnodes.plot_nodes_attr(graphs, feature="Age")
    plotgraph.plot_degree_distribution(degree_dis)

if __name__ == "__main__":
    main()
```

### 4.6 结果展示

#### 4.6.1 nodes

```python
'''
{0: ...
 1:['Karen Allen', '7467', 'starring', "American film actors;American stage actors;American video game actors;Bard College at Simon's Rock faculty;Illinois actors;People from Greene County, Illinois;Saturn Award winners;", []], 
 2: ...}
'''
```

#### 4.6.2 graphs

```python
'''
{0: ...
 1: ['Karen Allen', '7467', 'starring', "American film actors;American stage actors;American video game actors;Bard College at Simon's Rock faculty;Illinois actors;People from Greene County, Illinois;Saturn Award winners;", [19349, 11348, 16569, 582, 9023, 23255, 11814, 3869, 29127, 6106, 25265, 13214, 23127, 4562, 5465, 11190, 13175, 7922, 7353, 11257, 31026]], 
 2: ...
 }
'''
```

#### 4.6.3 node_degree

```python
node_degree = 21 # 节点ID为1的度为21
```

#### 4.6.4 print_node

```python
'''
Node ID: 1
Node Name: Karen Allen
Node Weight: 7467
Node Type: starring
Node Info: American film actors;American stage actors;American video game actors;Bard College at Simon's Rock faculty;Illinois actors;People from Greene County, Illinois;Saturn Award winners;
Vertices:
Node 1 <-> Node 19349
Node 1 <-> Node 11348
Node 1 <-> Node 16569
Node 1 <-> Node 582
Node 1 <-> Node 9023
Node 1 <-> Node 23255
Node 1 <-> Node 11814
Node 1 <-> Node 3869
Node 1 <-> Node 29127
Node 1 <-> Node 6106
Node 1 <-> Node 25265
Node 1 <-> Node 13214
Node 1 <-> Node 23127
Node 1 <-> Node 4562
Node 1 <-> Node 5465
Node 1 <-> Node 11190
Node 1 <-> Node 13175
Node 1 <-> Node 7922
Node 1 <-> Node 7353
Node 1 <-> Node 11257
Node 1 <-> Node 31026
'''
```

#### 4.6.5 cal_average_degree

```python
7.158416707989383 # 边去重后的结果
```

#### 4.6.6 cal_degree_distribution

```python
'''
{0: 6971, 1: 2913, 2: 3042, 3: 3139, 4: 3029, 5: 2840, 6: 2224, 7: 1699, 8: 1320, 9: 977, 10: 791, 11: 575, 12: 458, 13: 357, 14: 316, 15: 288, 16: 246, 17: 219, 18: 197, 19: 158, 20: 159, 21: 139, 22: 128, 23: 128, 24: 94, 25: 105, 26: 95, 27: 73, 28: 94, 29: 78, 30: 55, 31: 67, 32: 51, 33: 63, 34: 60, 35: 42, 36: 48, 37: 51, 38: 43, 39: 39, 40: 32, 41: 50, 42: 27, 43: 25, 44: 31, 45: 28, 46: 39, 47: 27, 48: 24, 49: 26, 50: 27, 51: 21, 52: 15, 53: 16, 54: 16, 55: 16, 56: 15, 57: 20, 58: 16, 59: 17, 60: 16, 61: 15, 62: 12, 63: 9, 64: 15, 65: 9, 66: 13, 67: 7, 68: 13, 69: 9, 70: 9, 71: 8, 72: 13, 73: 9, 74: 8, 75: 4, 76: 7, 77: 6, 78: 9, 79: 6, 80: 5, 81: 4, 82: 10, 83: 6, 84: 6, 85: 7, 86: 5, 87: 3, 88: 6, 89: 3, 90: 4, 91: 5, 92: 1, 93: 4, 94: 4, 95: 2, 96: 2, 97: 5, 98: 0, 99: 5, 100: 3, ...}
'''
```

#### 4.6.7 save_graph & load_graph

![image-20211023092644042](https://s2.loli.net/2022/01/29/d9qFfzKP4iAaVZ7.png)

#### 4.6.8 plot_nodes_attr

- feature = "Type"

![type](https://s2.loli.net/2022/01/29/a6uGcEVp9XlrTBt.png)

- feature = "Birth"

![birth](https://s2.loli.net/2022/01/29/GMFR8Pd7NBuiOlL.png)

- feature = "Age"

![age](https://s2.loli.net/2022/01/29/jqTfASRpUo6N3YG.png)

#### 4.6.9 plot_degree_distribution

![Nodes_Distribution](https://s2.loli.net/2022/01/29/X5TVs6xRv92aD4m.png)

### 4.7 Gephi绘制无向图

![screenshot_104534](https://s2.loli.net/2022/01/29/oU21vsxchlMG38L.png)

<img src="C:\Users\Liu_K\AppData\Roaming\Typora\typora-user-images\image-20211023105004520.png" alt="image-20211023105004520" style="zoom:50%;" />

- 下附Gephi生成的pdf

