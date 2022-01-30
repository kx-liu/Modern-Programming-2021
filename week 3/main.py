import re
import jieba
import requests
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pyecharts.charts import Geo
from pyecharts.charts import Map
from pyecharts.globals import GeoType
from pyecharts import options as opts

'''
    设置该列表为全局变量，最终每个元素将包含如下元素：
    [words_list], struct_time, [latitude, longtitude], emo_type, distance
'''
comms_list = []
emos_type = ["anger", "disgust", "fear", "joy", "sadness"]
emos_dic = {"anger":0, "disgust":1, "fear":2, "joy":3, "sadness":4, "none":5}
dist_dic = {"西城区":0, "东城区":1, "海淀区":2, "朝阳区":3, "石景山区":4, "丰台区":5}

def open_file1(emo):
    addr = "emotion_lexicon/" + emo + ".txt"
    with open(addr, encoding="utf-8") as f:
        emo_str = f.read()
    emo_list = list(emo_str.split("\n"))
    return emo_list

def get_emotion_lexicon_list():
    emos_list = []
    for emo in emos_type:
        emos_list.append(open_file1(emo))
    return emos_list

def open_file2():
    with open("weibo.txt", encoding="utf-8") as f:
        weibo_str = f.read()
    weibo_list_ori = list(weibo_str.split("\n"))
    return weibo_list_ori

def screening(weibo_list_ori, emos_list):
    '''
    用于清洗微博评论。

    填充全局变量comms_list，使其包含每条评论的分词结果、时间与地点，效果如下：
    comms_list = [[[words_list1], time1, [lat1, lon1]], ...]
    '''
    global comms_list
    for i in range(5):
        for word in emos_list[i]:
            jieba.add_word(word)
    for i in range(len(weibo_list_ori)):
        string = re.sub(r"(我在[这里]*)*:*http://t\.cn/[a-zA-Z0-9]{7}", "", weibo_list_ori[i])
        position = re.search(r"\[[0-9,\.\s]+\]", string).group()
        string = re.sub(r"\[[0-9,\.\s]+\]", "", string)
        time = re.search(r"(Fri|Sat|Sun)\sOct[A-za-z0-9:+\s]{23}", string).group()
        # if time is None: print(string)
        string = re.sub(r"(Fri|Sat|Sun)[A-za-z0-9:+\s]{27}", "", string)
        struct_time = time_standardize(time)
        words_list = divide_word(string)
        comm_list = [words_list, struct_time, eval(position)]
        comms_list.append(comm_list)

def divide_word(string):
    words = jieba.lcut(string)
    words_screened = []
    with open("stopwords_list.txt", encoding="utf-8") as f:
        sw_str = f.read()
    sw_list = list(sw_str.split("\n"))
    for word in words:
        if word in sw_list or word == "\t":
            continue
        words_screened.append(word)
    return words_screened

def time_standardize(time):
    temp = re.sub(r"\+0800\s", "", time)
    struct_time = datetime.datetime.strptime(temp, "%a %b %d %H:%M:%S %Y")
    return struct_time

def get_comment_emo(emos_list):
    global comms_list
    f = emo_analyser(emos_list)
    for i in range(len(comms_list)):
        emo_type = f(comms_list[i][0])
        comms_list[i].append(emo_type)

def emo_analyser(emos_list):
    def inner(comm):
        emo_vec = [0] * 5
        for word in comm:
            for i in range(5):
                if word in emos_list[i]:
                    emo_vec[i] += 1
                    break
        if sum(emo_vec) == 0:
            return 5
        max1 = max(emo_vec)
        max1_index = emo_vec.index(max1)
        # 判断是否有多个情绪为最大值
        emo_vec[max1_index] = 0
        max2 = max(emo_vec)
        if max1 == max2:
            return 5
        else:
            return max1_index
    return inner

def change_in_time(time_mode):
    fig, ax = plt.subplots()
    for i in range(5):
        f = emo_type1(emos_type[i])
        time_list, ratio_list = f(time_mode)
        ax.plot(time_list, ratio_list, lw=1.3)
    # 设置x轴主刻度格式
    day = mdates.DayLocator(interval=1) # 主刻度为天，间隔1天
    ax.xaxis.set_major_locator(day) # 设置主刻度
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # 设置副刻度格式
    hoursLoc = mdates.HourLocator(interval=4) # 为4小时为1副刻度
    ax.xaxis.set_minor_locator(hoursLoc)
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%S'))

    ax.tick_params(which='major',axis='x',labelsize=7,length=5,pad=11)
    ax.tick_params(which='minor',axis='x',labelsize=6,length=3)
    ax.tick_params(axis='y',labelsize=7)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.xaxis.grid(True, which="minor", lw=0.5, linestyle="--", color='0.8', zorder=1)
    ax.yaxis.grid(True, which="major", lw=0.5, linestyle="--", color='0.8', zorder=1)
    ax.legend(loc="upper right", frameon=False, labels=emos_type)
    ax.set_title("Emotion Changes in Time", fontsize=15)
    ax.set_xlabel("time", fontsize=10); ax.set_ylabel("emotion ratio", fontsize=10)
    # plt.savefig("Emotion_Changes_in_Time.png", dpi=1000)
    plt.show()

def emo_type1(emo):
    comms_list_sorted = sorted(comms_list, key=lambda x:x[1])
    def freq_mode(freq):
        emo_mode = emos_dic[emo]
        start_time = comms_list_sorted[0][1]
        ti = time_incrementor(freq)
        time_list = []
        ratio_list = []
        i = 0
        n = len(comms_list_sorted)
        while start_time < comms_list_sorted[-1][1]:
            time_list.append(start_time)
            end_time = ti(start_time)
            cnt_tot = 0
            cnt_emo = 0
            for j in range(i, n):
                if (start_time <= comms_list_sorted[j][1] < end_time):
                    cnt_tot += 1
                    if (comms_list_sorted[j][3] == emo_mode):
                        cnt_emo += 1
                    i += 1
                else:
                    break
            start_time = end_time
            if cnt_tot == 0:
                ratio_list.append(0)
            else:
                ratio_list.append(cnt_emo / cnt_tot)
        return time_list, ratio_list
    return freq_mode

def time_incrementor(freq):
    if freq == "second":
        return lambda x: x + datetime.timedelta(seconds=1)
    elif freq == "minute":
        return lambda x: x + datetime.timedelta(minutes=1)
    elif freq == "hour":
        return lambda x: x + datetime.timedelta(hours=1)
    elif freq == "day":
        return lambda x: x + datetime.timedelta(days=1)

def change_in_space(space_mode):
    fig, ax = plt.subplots()
    for i in range(5):
        f = emo_type2(emos_type[i], 0)
        radius_list, ratio_list = f(space_mode)
        # f = emo_type2(emos_type[i], 1)
        # radius_list, ratio_list = f()
        # print(i,":",ratio_list)
        ax.plot(ratio_list, lw=1.3)
    ax.set_xticklabels(radius_list, fontsize=9)
    ax.set_xticks([i for i in range(18)])
    # ax.set_xticks([0,1,2,3,4])
    ax.tick_params(axis='x',labelsize=7)
    ax.tick_params(axis='y',labelsize=7)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.xaxis.grid(True, lw=0.5, linestyle="--", color='0.8', zorder=1)
    ax.yaxis.grid(True, lw=0.5, linestyle="--", color='0.8', zorder=1)
    ax.legend(loc="upper right", frameon=False, labels=emos_type)
    ax.set_title("Emotion Changes in Space", fontsize=15)
    ax.set_xlabel("position", fontsize=10); ax.set_ylabel("emotion ratio", fontsize=10)
    # plt.savefig("Emotion_Changes_in_Space1.png", dpi=1000)
    # plt.savefig("Emotion_Changes_in_Space2.png", dpi=1000)
    plt.show()

def emo_type2(emo, flag):
    # flag = 0: 半径以step为步数递增
    # flag = 1: 半径以北京环数递增
    centre = find_centre()
    # print(centre)
    add_distance(centre)
    comms_list_sorted = sorted(comms_list, key=lambda x:x[4])
    emo_mode = emos_dic[emo]
    start_radius = 0
    radius_list = []
    ratio_list = []
    # print(comms_list_sorted[:20])
    # print(comms_list_sorted[-20:])
    def step_mode1(step):
        nonlocal start_radius, radius_list, ratio_list
        ri = radius_incrementor(step)
        i = 0
        n = len(comms_list_sorted)
        while start_radius <= 17:
            cnt_tot = 0
            cnt_emo = 0
            radius_list.append(start_radius)
            end_radius = ri(start_radius)
            for j in range(i, n):
                if (start_radius <= comms_list_sorted[j][4] < end_radius):
                    cnt_tot += 1
                    if (comms_list_sorted[j][3] == emo_mode):
                        cnt_emo += 1
                    i += 1
                else:
                    break
            if (cnt_tot == 0):
                ratio_list.append(0)
            else:
                ratio_list.append(cnt_emo / cnt_tot)
            # print("cnt_tot:", cnt_tot)
            # print("cnt_emo:", cnt_emo)
            start_radius = end_radius
        return radius_list, ratio_list
    def step_mode2():
        nonlocal start_radius, radius_list, ratio_list
        n = len(comms_list_sorted)
        i = 0
        k = 0
        step_list = [4.5, 7.5, 10, 15, 100]
        radius_list = ["Inside 2nd Ring Road", "2nd-3rd Ring Road", "3rd-4th Ring Road", 
                       "4th-5th Ring Road", "Outside 5th Ring Road"]
        while start_radius < comms_list_sorted[-1][4]:
            cnt_tot = 0
            cnt_emo = 0
            end_radius = step_list[k]
            k += 1
            for j in range(i, n):
                if (start_radius <= comms_list_sorted[j][4] < end_radius):
                    cnt_tot += 1
                    if (comms_list_sorted[j][3] == emo_mode):
                        cnt_emo += 1
                    i += 1
                else:
                    break
            if (cnt_tot == 0):
                ratio_list.append(0)
            else:
                ratio_list.append(cnt_emo / cnt_tot)
            # print("cnt_tot:", cnt_tot)
            # print("cnt_emo:", cnt_emo)
            start_radius = end_radius
        return radius_list, ratio_list
    if flag == 0: return step_mode1
    if flag == 1: return step_mode2

def find_centre():
    cum = np.array([0.0, 0.0])
    n = len(comms_list)
    for comm in comms_list:
        cum += np.array(comm[2])
    centre = (cum / n).tolist()
    return centre

def add_distance(centre):
    global comms_list
    for i in range(len(comms_list)):
        distance = distance_calculator(*centre, *comms_list[i][2])
        comms_list[i].append(distance)

def distance_calculator(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon1 - lon2
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371.136
    return c * r

def radius_incrementor(step):
    return lambda r: r + step

def map_visualization():
    g = Geo()
    g.add_schema(maptype="北京")
    data_pairs = [[], [], [], [], []]
    for i in range(len(comms_list)):
        if comms_list[i][3] == 5: continue # 无情绪，舍去
        coor = comms_list[i][2]
        g.add_coordinate(str(i), coor[1], coor[0])
        a = str(i)
        b = comms_list[i][3]
        data_pairs[b].append((a, b))
    i = 0
    col_list = ["#FB7C37", "#FEBD9A", "#843000", "#9fc186", "#90aacb"]
    for data_pair in data_pairs:
        if i == 5: symbol_size = 3
        else: symbol_size = 5
        g.add(emos_type[i], data_pair, type_=GeoType.SCATTER, color=col_list[4-i], 
               symbol_size=symbol_size, label_opts=opts.LabelOpts(is_show=False), is_large=True)
        i += 1
    g.set_global_opts(title_opts=opts.TitleOpts(title="Emotion Distribution in Beijing"))
    g.render("Emotion_Distribution.html")

def get_comment_dist():
    url = "https://api.map.baidu.com/geocoder?output=json&key=f247cdb592eb43ebac6ccd27f796e2d2&location="
    pattern = re.compile("(西城|东城|海淀|朝阳|石景山|丰台|大兴)区")
    with open("comm_list/district.txt", "w", encoding="utf-8") as f:
        for comms in comms_list:
            posi = str(comms[2])
            while True:
                response = requests.get(url + posi)
                addr = response.text
                if "DOCTYPE" in addr:
                    continue
                else:
                    distr = pattern.search(addr)
                    f.write(distr.group() + "\n")
                    break

def district_visualization():
    with open("comm_list/district.txt", encoding="utf-8") as f:
        string = f.read()
    dist_ls = string.split("\n")
    dist_emo_ls = [[0]*6, [0]*6, [0]*6, [0]*6, [0]*6]
    for i in range(len(comms_list)):
        if dist_ls[i] == "大兴区": continue # 大兴区仅有一个样本，舍去
        dist = dist_dic[dist_ls[i]]
        emo = comms_list[i][3]
        if emo == 5: continue # 无情绪，舍去
        dist_emo_ls[emo][dist] += 1
    dist_emo_ratio_ls = (np.array(dist_emo_ls) / np.sum(np.array(dist_emo_ls), axis=0) * 100).tolist()
    # print(dist_emo_ratio_ls)
    dist_dic_inv = {value: key for key, value in dist_dic.items()}
    emo_dic_inv = {value: key for key, value in emos_dic.items()}
    m = Map()
    for j in range(5):
        data_pair = [(dist_dic_inv[i], dist_emo_ratio_ls[j][i]) for i in range(6)]
        m.add(emo_dic_inv[j], data_pair, "北京")
    m.set_global_opts(
        title_opts=opts.TitleOpts(title="Emotion Distribution in Different Districts"), 
        visualmap_opts=opts.VisualMapOpts(max_=70, min_=0), 
        legend_opts=opts.LegendOpts(pos_bottom=0.2)
    )
    m.render("district_emotion.html")

def main():
    emos_list = get_emotion_lexicon_list()
    weibo_list_ori = list(set(open_file2())) # 去除重复评论
    screening(weibo_list_ori, emos_list)
    get_comment_emo(emos_list)
    # change_in_time(time_mode="hour")
    change_in_space(space_mode=1)
    # map_visualization()
    # get_comment_dist()
    # district_visualization()

if __name__ == "__main__":
    main()