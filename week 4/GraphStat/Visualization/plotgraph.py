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
    plt.savefig("Nodes_Distribution.png", dpi=800)
    plt.show()