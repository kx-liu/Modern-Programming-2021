import jieba
import numpy as np
import wordcloud
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import seaborn as sns

def open_file1():
    stop_words = []
    with open("stopwords_list.txt", encoding="utf-8") as f:
        stop_words = f.readlines()
    for i in range(len(stop_words)):
        stop_words[i] = stop_words[i].strip("\n")
    return stop_words

def open_file2(sw_ls):
    comments_ori = []
    comments = []
    with open("jd_comments.txt", encoding="utf-8") as f:
        comments_ori = f.readlines()
    for i in range(len(comments_ori)):
        comment_ori = comments_ori[i].strip("\n")
        comments_ori[i] = comment_ori
        comment = screening(comment_ori, sw_ls)
        comments.append(comment)
    return comments, comments_ori

def screening(comment, sw_ls):
    add_word = ["不错", "跑分"]
    for word in add_word:
        jieba.add_word(word)
    words = jieba.lcut(comment)
    words_screened = []
    for word in words:
        if word in sw_ls:
            continue
        words_screened.append(word)
    return words_screened

def frequency(comm_ls):
    freq_dic = {}
    for word in [e for ele in comm_ls for e in ele]:
        if word in freq_dic:
            freq_dic[word] += 1
        else:
            freq_dic[word] = 1
    freq_sorted_temp = sorted(freq_dic.items(), key=lambda x:x[1], reverse=True)
    freq_sorted = []
    for tup in freq_sorted_temp:
        if tup[1] < 50:
            continue
        freq_sorted.append(tup)
    # print(freq_sorted)
    # 导出词频，核验特征词
    # with open("frequency.txt", "w", encoding="utf-8") as f:
    #     for tup in freq_sorted:
    #         f.write(tup[0] + "\t" + str(tup[1]) + "\n")
    return freq_sorted, freq_dic

def feature_filter(freq_sorted):
    my_stopwords_list = [" ", "不", "没", "京东", "感觉", "说", "上", "东西", "看", 
                         "后", "hellip", "一下", "才", "下", "一次", "知道", "卖家", 
                         "现在", "装", "来说", "一点", "已经", "秒", "之前", "打开", 
                         "货", "觉得", "最后", "款"] # 保留副词(程度词)
    features_ls = []
    for tup in freq_sorted:
        if tup[0] in my_stopwords_list:
            continue
        features_ls.append(tup)
    # print(features_ls)
    return features_ls

def features_vector(comm_ls, feats_ls):
    feats_vec = []
    n = len(feats_ls)
    feats = [tup[0] for tup in feats_ls]
    for comm in comm_ls:
        temp = [0 for i in range(n)]
        for word in comm:
            if word in feats:
                if temp[feats.index(word)] == 1:
                    continue
                temp[feats.index(word)] += 1
        feats_vec.append(temp)
    return feats_vec

def Euclid(vec1, vec2):
    return (sum([(a - b) ** 2 for (a, b) in zip(vec1, vec2)])) ** 0.5

def distance(feats_vec):
    n = len(feats_vec)
    dis_dic = {}
    dis_matrix = np.array([[0 for i in range(n)] for j in range(n)])
    for i in range(n):
        for j in range(i + 1, n):
            key = (i, j)
            value = Euclid(feats_vec[i], feats_vec[j])
            dis_dic[key] = value
            dis_matrix[i][j] = value
            dis_matrix[j][i] = value
    sns.heatmap(data=dis_matrix)
    plt.title("Distance Heatmap")
    plt.savefig("heatmap.png", dpi = 1500)
    plt.show()
    dis_dic_sorted = sorted(dis_dic.items(), key=lambda x:x[1], reverse=False)
    # with open("rank.txt", "w") as f:
    #     for tup in dis_dic_sorted:
    #         f.write(str(tup[0]) + "\t" + str(round(tup[1], 3)) + "\n")
    return dis_dic_sorted

def centre(feats_vec):
    feats_vec_T = np.array(feats_vec).T
    row, col = np.shape(feats_vec_T)
    ones = np.array([1 for i in range(col)]).reshape(col, 1)
    sums = np.matmul(feats_vec_T, ones)
    centre_vec = np.transpose(sums / col)
    return centre_vec

def draw_wordcloud(freq_dic):
    my_stopwords_list = [" ", "不", "没", "京东", "感觉", "说", "上", "东西", "看", 
                         "后", "hellip", "一下", "才", "下", "一次", "知道", "卖家", 
                         "现在", "装", "来说", "一点", "已经", "秒", "之前", "打开", 
                         "很", "货", "觉得", "最后", "款", "还", "非常", "没有", "收到", 
                         "都", "使用", "送", "有点", "挺", "比较", "会", "再", "不是", 
                         "真的"] # 进一步筛选
    wd_dic = {}
    for key in freq_dic:
        if freq_dic[key] > 50 and key not in my_stopwords_list:
            wd_dic[key] = freq_dic[key]
        
    wc = wordcloud.WordCloud(
        font_path = "C:\Windows\Fonts\simhei.ttf",
        max_words = 200,
        max_font_size = 100,
        scale = 8
    )
    wc.generate_from_frequencies(wd_dic)
    plt.imshow(wc)
    plt.axis("off")
    plt.savefig("wc.png", dpi = 1500)
    plt.show()

def manhattan_distance(x, y):
    return np.sum(abs(x - y))

def clustering(feats_vec):
    # 绘制碎石图确定聚为几类
    # distance = []
    # k = []
    # feats_vec = np.array(feats_vec)
    # for n_clusters in range(1, 21):
    #     kmeans = KMeans(n_clusters).fit(feats_vec)
    #     distance_sum = 0
    #     for i in range(n_clusters):
    #         group = kmeans.labels_ == i
    #         members = feats_vec[group,:]
    #         for v in members:
    #             distance_sum += manhattan_distance(np.array(v), kmeans.cluster_centers_[i])
    #     distance.append(distance_sum)
    #     k.append(n_clusters)
    # plt.scatter(k, distance)
    # plt.plot(k, distance)
    # plt.xlabel("k"); plt.ylabel("distance"); plt.title("scree plot")
    # plt.show()
    kmeans = KMeans(n_clusters=9).fit(np.array(feats_vec))
    centers = kmeans.cluster_centers_
    labels = {i: np.where(kmeans.labels_ == i)[0] for i in range(9)}
    # print(labels)

    pca = PCA(n_components=2)
    X_reduced = pca.fit_transform(np.array(feats_vec))
    # print(pca.explained_variance_ratio_)
    # plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=kmeans.labels_, cmap=plt.cm.Set1)
    # plt.show()
    return labels, centers, X_reduced

def most_featured_comment(comm_ls_ori, centers, labels, feats_vec):
    i = 0
    dis_cen_dic_ls = [{}, {}, {}, {}, {}, {}, {}, {}, {}]
    for j in range(len(dis_cen_dic_ls)):
        indexs = labels[j].tolist()
        # print(indexs)
        for index in indexs:
            dis = Euclid(feats_vec[index], centers[i])
            dis_cen_dic_ls[i][index] = dis
        i += 1
    for dic in dis_cen_dic_ls:
        dic_sorted = sorted(dic.items(), key = lambda x:x[1])
        # print(comm_ls_ori[dic_sorted[0][0]])
    
def main():
    # 打开stopwords_list.txt
    sw_ls = open_file1()
    # 打开jd_comments.txt并进行分词处理
    comm_ls, comm_ls_ori = open_file2(sw_ls)
    # 词频统计并排序
    freq_sorted, freq_dic = frequency(comm_ls)
    # 取高频词并自定义筛选-->特征集
    feats_ls = feature_filter(freq_sorted)
    # 构建特征集向量
    feats_vec = features_vector(comm_ls, feats_ls)
    # 计算每条评论间距离，导出rank.txt距离排名
    dis_dic_sorted = distance(feats_vec)
    # 计算全部评论的“物理”重心
    centre_vec = centre(feats_vec)
    # 绘制词云图
    # draw_wordcloud(freq_dic)
    # PCA + clustering
    labels, centers, X_reduced = clustering(feats_vec)
    # 确定距离四类评论的中心最近的样本点
    most_featured_comment(comm_ls_ori, centers, labels, feats_vec)

if __name__ == '__main__':
    main()