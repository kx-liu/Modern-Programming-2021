import re

file  = "news_sohusite_xml.dat"

def get_line():
    line_cnt = 0
    with open(file, encoding="GB18030") as f:
        for line in f:
            line_cnt += 1
    return line_cnt

def write():
    # 一个文件存10000条新闻
    with open(file, encoding="GB18030") as f:
        for j in range(1411996 // 10000):
            with open(f"./news/{j+1}.txt", "w", encoding="GB18030") as news:
                for i in range(60000):
                    string = f.readline()
                    if "<content>" in string:
                        string = re.sub("<content>|</content>", "", string)
                        if string == "": break
                        news.write(string)
                    else:
                        continue

# print(get_line()) # 8471976行，1411996条新闻
write()