## 第十次作业 抽象类

### 10.1 大致框架

```python
class Plotter(metaclass=abc.ABCMeta):
    '''
    通过不同子类的具体实现来支持多类型数据的绘制，
    至少包括数值型数据，文本，图片等
    '''
    @abc.abstractmethod
    def plot(self, data, *args, **kwargs):
        pass

class PointPlotter(Plotter):
    '''
    实现数据点型数据的绘制，
    即输入数据为[(x,y)...]型，每个元素为一个Point类的实例
    '''
    def plot(self, data, *args, **kwargs):
        pass

class ArrayPlotter(Plotter):
    '''
    实现多维数组型数据的绘制，
    即输入数据可能是[[x1,x2...],[y1,y2...]]或者[[x1,x2...],[y1,y2...],[z1,z2...]]
    '''
    def plot(self, data, *args, **kwargs):
        pass

    def _kmeans(self, data):
        pass

    def _dim_reduction(self, data):
        '''
        多维数组超过3维，
        降维并绘制
        '''
        pass

class TextPlotter(Plotter):
    '''
    实现文本型数据的绘制，
    即输入数据为一段或多段文本，应进行切词，关键词选择（根据频率或tf-idf)，继而生成词云
    '''
    def plot(self, data, *args, **kwargs):
        pass

class ImagePlotter(Plotter):
    '''
    实现图片型数据的绘制，
    即输入数据为图片的路径或者图片内容（可以是多张图片），呈现图片并按某种布局组织（如2x2等)
    '''
    def plot(self, data, *args, **kwargs):
        pass

class GifPlotter(Plotter):
    '''
    支持一组图片序列的可视化（通过文件路径或图片内容输入），
    但输出是gif格式的动态图
    '''
    def plot(self, data, *args, **kwargs):
        pass

    def _video(self, data):
        '''
        输入是一段落视频，
        通过帧采样，将视频绘制为gif并输出为微信表情包
        '''
        pass

class MusicPlotter(Plotter):
    '''
    输入是一段音频（比如mp3文件）
    '''
    pass

class Point(object):
    '''
    实现Point类，
    实例化后提供给PointPlotter与ArrayPlotter
    '''
    pass
```

### 10.2 Plotter基类

```python
class Plotter(metaclass=abc.ABCMeta):
    '''
    通过不同子类的具体实现来支持多类型数据的绘制，
    至少包括数值型数据，文本，图片等
    '''
    @abc.abstractmethod
    def plot(self, data, *args, **kwargs):
        pass
```

- 基类中不实现具体功能

### 10.3 PointPlotter子类与Point类

#### 10.3.1 Point类

```python
class Point(object):
    '''
    实现Point类，
    实例化后提供给PointPlotter
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return "({:.2f}, {:.2f})".format(self.x, self.y)
```

#### 10.3.2 PointPlotter子类

```python
class PointPlotter(Plotter):
    '''
    实现数据点型数据的绘制，
    即输入数据为[(x,y)...]型，每个元素为一个Point类的实例
    '''
    def plot(self, data, *args, **kwargs):
        x_list = []
        y_list = []
        for point in data:
            x_list.append(point.x)
            y_list.append(point.y)
        plt.scatter(x_list, y_list)
        plt.title("PointPlotter")
        plt.savefig("PointPlotter.png", dpi=1000)
        plt.show()
```

- 类的实例化

```python
points = []
for i in range(10):
    points.append(Point(random.randint(1,10), random.randint(1,10)))
pp = PointPlotter()
pp.plot(points)
```

<img src="https://s2.loli.net/2022/01/29/95OogIKlSuNrHq1.png" alt="PointPlotter" style="zoom: 10%;" />

### 10.4 ArrayPlotter子类

```python
class ArrayPlotter(Plotter):
    '''
    实现多维数组型数据的绘制，
    即输入数据可能是[[x1,x2...],[y1,y2...]]或者[[x1,x2...],[y1,y2...],[z1,z2...]]
    '''
    def plot(self, data, *args, **kwargs):
        if len(data[0]) >= 3:
            fig = plt.figure()
            ax = Axes3D(fig)
            if len(data[0]) > 3:
                data, labels = ArrayPlotter._dim_reduction(self, data)
                ax.scatter(data[:, 0], data[:, 1], data[:, 2], c=labels, cmap=plt.cm.Set1)
            elif len(data[0]) == 3:
                data = np.array(data)
                ax.scatter(data[:, 0], data[:, 1], data[:, 2], cmap=plt.cm.Set1)
        else:
            data = np.array(data)
            plt.scatter(data[:, 0], data[:, 1], cmap=plt.cm.Set1)
        plt.savefig("ArrayPlot.png", dpi=1000)
        plt.show()

    def _kmeans(self, data):
        km = KMeans(n_clusters=3, max_iter=3).fit(np.array(data))
        return km.labels_

    def _dim_reduction(self, data):
        '''
        多维数组超过3维，
        降维并绘制
        '''
        labels = ArrayPlotter._kmeans(self, data)
        # tsne = TSNE(n_components=2, init="pca", random_state=0).fit(np.array(data))
        # df = pd.DataFrame(tsne.embedding_)
        # df["labels"] = labels
        # df1 = df[df["labels"] == 0]
        # df2 = df[df["labels"] == 1]
        # df3 = df[df["labels"] == 2]
        # plt.plot(df1[0], df1[1], "bo", df2[0], df2[1], "r*", df3[0], df3[1], "gD")
        # plt.show()
        pca = PCA(n_components=3)
        X_reduced = pca.fit_transform(np.array(data))
        return X_reduced, labels
```

#### 10.4.1 维数为2

- 类的实例化

```python
array = []
for i in range(10):
    tmp = [random.randint(0, 3) for j in range(2)]
    array.append(tmp)
for i in range(10):
    tmp = [random.randint(3, 6) for j in range(2)]
    array.append(tmp)
for i in range(10):
    tmp = [random.randint(6, 9) for j in range(2)]
    array.append(tmp)
ap = ArrayPlotter()
ap.plot(array)
```

<img src="https://s2.loli.net/2022/01/29/kNe3qLSAofP7Y8n.png" alt="ArrayPlotter" style="zoom:10%;" />

#### 10.4.2 维数为3

- 类的实例化

```python
array = []
for i in range(10):
    tmp = [random.randint(0, 3) for j in range(3)]
    array.append(tmp)
for i in range(10):
    tmp = [random.randint(3, 6) for j in range(3)]
    array.append(tmp)
for i in range(10):
    tmp = [random.randint(6, 9) for j in range(3)]
    array.append(tmp)
ap = ArrayPlotter()
ap.plot(array)
```

<img src="https://s2.loli.net/2022/01/29/hJ3oqeEy4u95Yz6.png" alt="ArrayPlotter3" style="zoom:10%;" />

#### 10.4.3 维数大于3

- 类的实例化

```python
array = []
for i in range(10):
    tmp = [random.randint(0, 3) for j in range(10)]
    array.append(tmp)
for i in range(10):
    tmp = [random.randint(3, 6) for j in range(10)]
    array.append(tmp)
for i in range(10):
    tmp = [random.randint(6, 9) for j in range(10)]
    array.append(tmp)
ap = ArrayPlotter()
ap.plot(array)
```

<img src="https://s2.loli.net/2022/01/29/psRr1Aa2qZFT5ze.png" alt="ArrayPlotter10" style="zoom:10%;" />

### 10.5 TextPlotter子类

```python
class TextPlotter(Plotter):
    '''
    实现文本型数据的绘制，
    即输入数据为一段或多段文本，应进行切词，关键词选择（根据频率或tf-idf)，继而生成词云
    '''
    def plot(self, data, *args, **kwargs):
        stopwords_list = kwargs["stopwords_list"]
        add_word = kwargs["add_word"]
        for word in add_word:
            jieba.add_word(word)
        word_list = jieba.lcut(data)
        freq_dic = {}
        for word in word_list:
            if word in freq_dic:
                freq_dic[word] += 1
            else:
                freq_dic[word] = 1
        wd_dic = {}
        for key in freq_dic:
            if freq_dic[key] > 10 and key not in stopwords_list:
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
        plt.savefig("wc.png", dpi=1500)
        plt.show()
```

- 类的实例化（十九届六中全会公报）

```python
with open("jueyi.txt", encoding="utf-8") as f:
    string = f.read()
string = re.sub("\\n", "", string)
tp = TextPlotter()
stopwords_list = ["，", "、", "的", "。", "和", "\u3000", "了", "在", "是", "为", "“", "”", "上", "以", 
                    "（", "）", "到", "从", "等", "不", "对", "大", "把", "中", "就", "同", "由", "；", 
                    "以来", "之", "二", "向", "走", "〇", "要"]
add_word = ["新时代", "人类命运共同体", "一个中国"]
tp.plot(string, stopwords_list=stopwords_list, add_word=add_word)
```

<img src="D:\vscode py\现代程设\week 10\TextPlotter.png" alt="TextPlotter" style="zoom:10%;" />

### 10.6 ImagePlotter子类

```python
class ImagePlotter(Plotter):
    '''
    实现图片型数据的绘制，
    即输入数据为图片的路径或者图片内容（可以是多张图片），呈现图片并按某种布局组织（如2x2等)
    '''
    def plot(self, data, *args, **kwargs):
        suffix = args[0]
        name_list = os.listdir(data)
        images_list = []
        for name in name_list:
            ls = name.split(".")
            if suffix in ls[1].lower():
                images_list.append(Image.open(data+"\\"+name))
        for i in range(len(name_list)):
            if i == 3 * 3: break
            plt.subplot(3, 3, i+1)
            plt.imshow(images_list[i])
            plt.axis("off")
        plt.show()
```

- 类的实例化

```python
ip = ImagePlotter()
ip.plot("D:\\vscode py\\现代程设\\week 10\\images\\", "jpg", nrow=3, ncol=3)
```



<img src="D:\vscode py\现代程设\week 10\ImagePlotter.png" alt="ImagePlotter" style="zoom:10%;" />

### 10.7 GifPlotter子类

```python
class GifPlotter(Plotter):
    '''
    支持一组图片序列的可视化（通过文件路径或图片内容输入），
    但输出是gif格式的动态图
    '''
    def plot(self, data, *args, **kwargs):
        if args[0] == "video":
            data = GifPlotter._video(self, data)
        name_list = os.listdir(data)
        images_list = []
        for name in name_list:
            ls = name.split(".")
            if args[0] in ls[1].lower():
                images_list.append(imageio.imread(data+"\\"+name))
        imageio.mimsave("T&J.gif", images_list, "GIF", duration=0.2)

    def _video(self, data):
        '''
        输入是一段落视频，
        通过帧采样，将视频绘制为gif并输出为微信表情包
        '''
        vidcap = cv2.VideoCapture(data)
        success, image = vidcap.read()
        print("read a new frame: ", success)
        cnt = 0
        while success:
            if cnt % 3 == 0:
                cv2.imwrite(f"D:\\vscode py\\gifpics\\{cnt//3+1}.jpg", image)
            success, image = vidcap.read()
            print("read a new frame: ", success)
            cnt += 1
        return "D:\\vscode py\\gifpics\\"
```

 #### 10.7.1 一组图片

- 类的实例化

```python
gp = GifPlotter()
gp.plot("D:\\vscode py\\gifpics\\", "jpg")
```

<img src="https://s2.loli.net/2022/01/29/RboCa6y93EZGudW.png" alt="image-20211204133241958" style="zoom: 33%;" />

<img src="https://s2.loli.net/2022/01/29/uFmrt9sz4DIvMkY.gif" style="zoom:33%;" />

<center>（此处为动图）</center>

#### 10.7.2 一个视频

- 类的实例化（用的例子同为Tom and Jerry片段）

```python
gp = GifPlotter()
gp.plot("D:\\vscode py\\现代程设\\week 10\\T&J.mp4", "video")
```

<img src="https://s2.loli.net/2022/01/29/uFmrt9sz4DIvMkY.gif" style="zoom:33%;" />

<center>（此处为动图）</center>

### 10.8 MusicPlotter子类

```python
class MusicPlotter(Plotter):
    '''
    输入是一段音频（比如mp3文件）
    '''
    def plot(self, data, *args, **kwargs):
        y, sr = librosa.load(data, sr=None)
        librosa.display.waveplot(y, sr=22050)
        plt.show()
        plt.savefig("MusicPlotter.png")
```

- 类的实例化

```python
mp = MusicPlotter()
mp.plot("D:\\vscode py\\现代程设\\week 10\\champion.wav")
```

<img src="https://s2.loli.net/2022/01/29/5pfohg13YPLrZam.png" alt="MusicPlotter" style="zoom:10%;" />

