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
        plt.savefig("type.png", dpi=800)
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
        plt.xticks(rotation=20, fontsize=5)
        plt.savefig("birth.png", dpi=800)
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
        plt.xticks(rotation=20, fontsize=6)
        plt.savefig("age.png", dpi=800)
        plt.show()
