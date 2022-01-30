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