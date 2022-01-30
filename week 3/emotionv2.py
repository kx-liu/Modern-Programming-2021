import re

def get_comms_list():
    comms_list = []
    with open("weibo.txt", encoding="utf-8") as f:
        weibo_str = f.read()
    weibo_list_ori = list(weibo_str.split("\n"))
    for string in weibo_list_ori:
        string = re.sub(r"(我在[这里]*)*:*http://t\.cn/[a-zA-Z0-9]+", "", string)
        string = re.sub(r"\[[0-9,\.\s]+\]", "", string)
        string = re.sub(r"(Fri|Sat|Sun)\sOct[A-za-z0-9:+\s]{23}", "", string)
        string = re.sub(r"\s(\t)+", "", string)
        comms_list.append(string)
    return comms_list