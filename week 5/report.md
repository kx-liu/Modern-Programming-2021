## 第五周作业 实现文本处理的Tokenizer类

### 5.1 类框架展示

```python
class Tokenizer:
    '''
    按照预先定义好的词典，把文本编码成整数序列;
    为使句子长度整齐，规定特殊号码[PAD]=0，代表填充位。
    '''
    def __init__(self, chars, coding="c", PAD=0):
        '''
        构建词典，即构建汉字到正整数的唯一映射
        '''
    def tokenize(self, sentence):
        '''
        输入一句话，返回分词（字）后的字符列表(list_of_chars)
        '''
    def encode(self, list_of_chars):
        '''
        输入字符（字或者词）的字符列表，返回转换后的数字列表(tokens)
        '''
    def trim(self, tokens, seq_len):
        '''
        输入数字列表tokens，整理数字列表的长度；
        不足seq_len的部分用PAD补足，超过的部分截断。
        '''
    def decode(self, tokens):
        '''
        将模型输出的数字列表翻译回句子
        '''
    def tokens_equal_to_seq_len(self, seq_len):
        '''
        返回所有文本(chars)的长度为seq_len的tokens
        '''
    def def seq_len_distribution(self):
        '''
        返回所有文本(chars)的最大长度频数，并绘制长度频度分布图
        '''
```

### 5.2 各方法功能实现

#### 5.2.0 初始化\__init__

```python
def __init__(self, chars, coding="c", PAD=0):
        '''
        构建词典，即构建汉字到正整数的唯一映射
        '''
        self.chars = chars
        self.coding = coding
        dic = {"[PAD]": 0}
        if coding == "c":
            i = 1
            for char in chars:
                c_list = jieba.lcut(char)
                # 将中文单词分解为单字，英文不变
                for c in c_list:
                    if 97 <= ord(c[0]) <= 122 or 65 <= ord(c[0]) <= 90:
                        # 英文情况
                        if c not in dic: dic[c] = i; i += 1
                    else:
                        # 中文、标点符号等情况
                        for c_chi in c:
                            if c_chi not in dic: dic[c_chi] = i; i += 1
            self.dic = dic
        if coding == "w":
            i = 1
            for char in chars:
                char_list = jieba.lcut(char)
                for c in char_list:
                    if c in dic: continue
                    else: dic[c] = i; i += 1
            self.dic = dic
```

- 注意到weibo评论中存在中英文混合的情形，利用`jieba`分词对于中英文可分离且英文单词逐词分词的特性，首先将每条评论进行`jieba`分词，得到中英文混合的分词列表`c_list`；
  - `coding == "c"`：遍历`c_list`，判断其是否为英文，若为英文则直接加入字典，若为中文则进一步按字分词，逐字加入字典；
  - `coding == "w"`：直接加入字典。

- 将原始字符串列表`chars`、`coding`、构建的字典`dic`存入`self`中，方便类中方法的调用。

#### 5.2.1 tokenize

```python
def tokenize(self, sentence):
        '''
        输入一句话，返回分词（字）后的字符列表(list_of_chars)
        '''
        list_of_chars = []
        if self.coding == "c":
            c_list = jieba.lcut(sentence)
            for c in c_list:
                if 97 <= ord(c[0]) <= 122 or 65 <= ord(c[0]) <= 90:
                    # 英文情况
                    list_of_chars.append(c)
                else:
                    # 中文、标点符号等情况
                    for c_chi in c:
                        list_of_chars.append(c_chi)
            return list_of_chars
        if self.coding == "w":
            c_list = jieba.lcut(sentence)
            for c in c_list:
                list_of_chars.append(c)
            return list_of_chars
```

- 与`__init__`类似，同样分为`coding == "c"`和`coding == "w"`两种情况进行处理，同时要考虑中英混合的处理；
- 返回`list_of_chars`，即分词（字）后的字符列表。

#### 5.2.2 encode

```python
def encode(self, list_of_chars):
        '''
        输入字符（字或者词）的字符列表，返回转换后的数字列表(tokens)
        '''
        tokens = []
        for char in list_of_chars:
            tokens.append(self.dic[char])
        return tokens
```

- 调用`self.dic`已完成字符到数字的映射；
- 返回`tokens`，即转换后的数字列表。

#### 5.2.3 trim

```python
def trim(self, tokens, seq_len):
        '''
        输入数字列表tokens，整理数字列表的长度；
        不足seq_len的部分用PAD补足，超过的部分截断。
        '''
        n = len(tokens)
        if n <= seq_len:
            # 需要补足
            trimmed_tokens = tokens + ["PAD"] * (seq_len - n)
        else:
            # 需要截断
            trimmed_tokens = tokens[:seq_len]
        return trimmed_tokens
```

- 返回`trimmed_tokens`，即被截断或补足后的数字列表。

#### 5.2.4 decode

```python
def decode(self, tokens):
        '''
        将模型输出的数字列表翻译回句子
        '''
        sentence = ""
        dic_inv = {value: key for key, value in self.dic.items()}
        for num in tokens:
            if num == "PAD": sentence += "[PAD]"; continue
            sentence += dic_inv[num]
        return sentence
```

- 构建`self.dic`的逆映射`dic_inv`，以实现由数字到字符的映射；
- 返回`sentence`，即`tokens`到`sentence`的逆映射。

#### 5.2.5 tokens_equal_to_seq_len

```python
def tokens_equal_to_seq_len(self, seq_len):
        '''
        返回所有文本(chars)的长度为seq_len的tokens
        '''
        tokens_list = []
        for char in self.chars:
            list_of_chars = self.tokenize(char)
            if len(list_of_chars) == seq_len:
                tokens = self.encode(list_of_chars)
                tokens_list.append(tokens)
        return tokens_list
```

- 返回`tokens_list`，即`chars`中的长度为`seq_len`的`tokens`。

#### *5.2.6 seq_len_distribution

```python
def seq_len_distribution(self, isplot=False):
        '''
        返回所有文本(chars)的最大长度频数，并绘制长度频度分布图
        '''
        dis = [0] * 200
        for char in self.chars:
            length = len(self.tokenize(char))
            # if "分享图片" in char and length == 4: continue
            dis[length] += 1
        max_seq_len = dis.index(max(dis))
        if isplot == True:
            x = [i for i in range(200)]
            plt.bar(x, dis)
            plt.xlabel("seq_len"); plt.ylabel("frequency")
            plt.title("Seq_len Distribution")
            plt.savefig("seq_len_distribution", dpi=800)
            plt.show()
            return max_seq_len
        else:
            return max_seq_len
```

- 返回`chars`的最大长度频数，若参数`isplot == True`则绘制长度频数分布图，默认为`False`，即不绘制。

### 5.3 main函数与包管理

```python
import sys; sys.path.append("D:\\vscode py\\现代程设\\week 3")
import emotionv2
import jieba

def main():
    comms_list = emotionv2.get_comms_list()
    t = Tokenizer(comms_list, coding="c")
    list_of_chars = t.tokenize(comms_list[1]) # ; print(list_of_chars)
    tokens = t.encode(list_of_chars) # ; print(tokens)
    trimmed_tokens = t.trim(tokens, 20) # ; print(trimmed_tokens)
    sen = t.decode(trimmed_tokens) # ; print(sen)
    tokens_list = t.tokens_equal_to_seq_len(20)
    # for i in range(10):
    #     print(tokens_list[i])
    max_seq_len = t.seq_len_distribution(isplot=True) ; print(max_seq_len)
if __name__ == '__main__':
    main()
```

```python
# emotionv2.py
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
```

- 由于用到第三周的数据集，考虑到数据处理部分的重合，直接`import`第三周作业代码`emotionv2.py`（经简单修改的version2）作为`module`以实现文件的读取与数据清洗；
- 建立实例`t = Tokenizer(comms_list, coding)`。

### 5.4 结果展示

#### 5.4.1 t.tokenize()

- `coding == "c"`

```python
# list_of_chars = t.tokenize(comms_list[1])
>>> print(list_of_chars)
[' ', '@', '高', '娅', '洁', ' ', '是', '黑', '妹', '吗', '？']
```

- `coding == "w"`

```python
# list_of_chars = t.tokenize(comms_list[1])
>>> print(list_of_chars)
[' ', '@', '高娅洁', ' ', '是', '黑妹', '吗', '？']
```

#### 5.4.2 t.encode

- `coding == "c"`

```python
# tokens = t.encode(list_of_chars)
>>> print(tokens)
[5, 6, 7, 8, 9, 5, 10, 11, 12, 13, 14]
```

- `coding == "w"`

```python
# tokens = t.encode(list_of_chars)
>>> print(tokens)
[3, 4, 5, 3, 6, 7, 8, 9]
```

#### 5.4.3 t.trim

假定截长补短至长度为20。

- `coding == "c"`

```python
# trimmed_tokens = t.trim(tokens, 20)
>>> print(trimmed_tokens)
[5, 6, 7, 8, 9, 5, 10, 11, 12, 13, 14, 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD']
```

- `coding == "w"`

```python
# trimmed_tokens = t.trim(tokens, 20)
>>> print(trimmed_tokens)
[3, 4, 5, 3, 6, 7, 8, 9, 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD', 'PAD']
```

#### 5.4.4 t.decode

- `coding == "c"`

```python
# sen = t.decode(trimmed_tokens)
>>> print(sen)
 @高娅洁 是黑妹吗？[PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD]
```

- `coding == "w"`

```python
# sen = t.decode(trimmed_tokens)
>>> print(sen)
 @高娅洁 是黑妹吗？[PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD]
```

#### 5.4.5 t.tokens_equal_to_seq_len

- `coding == "c"`

```python
# tokens_list = t.tokens_equal_to_seq_len(20)
>>> for i in range(10):
...     print(tokens_list[i])
[256, 286, 167, 48, 146, 540, 931, 34, 76, 70, 929, 79, 76, 70, 929, 79, 76, 70, 929, 79]
[1176, 115, 403, 1177, 167, 167, 167, 1176, 921, 208, 115, 167, 167, 167, 573, 19, 88, 438, 167, 167]
[48, 284, 785, 262, 105, 27, 371, 496, 37, 1404, 1405, 962, 1406, 262, 1407, 1408, 27, 366, 248, 130]
[48, 53, 141, 211, 102, 110, 215, 216, 1338, 591, 1446, 492, 484, 1052, 591, 1446, 492, 484, 745, 110]
[1161, 56, 293, 27, 405, 915, 37, 530, 56, 293, 27, 322, 915, 24, 141, 728, 1305, 103, 27, 14]
[1305, 137, 1071, 1072, 48, 37, 764, 380, 1571, 27, 766, 214, 65, 380, 1571, 152, 459, 658, 1052, 454]
[1605, 464, 34, 37, 141, 232, 256, 130, 130, 130, 5, 5, 6, 5, 133, 501, 26, 1606, 204, 1607]
[210, 227, 104, 94, 37, 365, 296, 408, 71, 1695, 1629, 1695, 1629, 37, 571, 46, 365, 210, 227, 24]
[324, 256, 48, 193, 139, 34, 877, 877, 27, 909, 762, 926, 6, 21, 1708, 1708, 27, 1200, 69, 1402]
[94, 94, 27, 46, 1366, 360, 37, 245, 845, 146, 68, 93, 454, 208, 37, 337, 1107, 707, 176, 14]
```

- `coding == "w"`

```python
# tokens_list = t.tokens_equal_to_seq_len(20)
>>> for i in range(10):
...     print(tokens_list[i])
[491, 3, 492, 3, 493, 3, 494, 3, 495, 3, 496, 49, 497, 51, 49, 497, 51, 49, 497, 51]
[261, 510, 6, 566, 61, 1215, 17, 1216, 86, 86, 49, 1217, 1218, 51, 49, 1219, 51, 49, 1220, 51]
[1427, 17, 1428, 6, 946, 1429, 17, 1430, 77, 1431, 24, 1432, 91, 151, 1433, 94, 17, 1434, 24, 86]
[1740, 132, 1781, 278, 1782, 17, 1783, 1784, 1785, 1786, 1787, 24, 69, 35, 1788, 373, 408, 17, 412, 1789]
[2212, 2213, 2214, 24, 959, 219, 490, 2215, 24, 2216, 473, 2217, 24, 2218, 2219, 974, 24, 2220, 2221, 15]
[1782, 2339, 357, 153, 2340, 2341, 2342, 24, 2339, 649, 2341, 24, 25, 926, 41, 35, 1782, 2343, 2344, 17]
[1524, 92, 2854, 2855, 22, 24, 1139, 2856, 679, 2857, 302, 24, 2858, 2859, 640, 352, 2860, 17, 2861, 66]
[61, 508, 22, 24, 1055, 3411, 22, 24, 3412, 679, 3413, 22, 246, 24, 1444, 186, 3414, 49, 3082, 51]
[4064, 3, 547, 3, 4065, 3, 4066, 3, 4067, 3, 494, 2740, 280, 2740, 3, 3, 4068, 3, 4, 4069]
[103, 4213, 153, 3469, 17, 678, 4214, 1098, 17, 678, 24, 263, 24, 69, 4215, 17, 678, 169, 169, 169]
```

#### *5.4.6 t.seq_len_distribution

- `coding == "c"`

  ```python
  max_seq_len = t.seq_len_distribution(isplot=True)
  >>> print(max_seq_len)
  4
  ```

  ![seq_len_distribution](https://s2.loli.net/2022/01/29/QOMbUX5RAKa1Cvq.png)

  - 我们发现`seq_len = 4`时频数取最大值，从图中不难看出该点为**异常点**。考虑到数据集中**评论“分享图片”占据较多评论**，若`Tokenizer`将大量“分享图片”作为基准则失去其意义，故做出判断

    `if "分享图片" in char and length == 4: continue`

  - 此时，再次执行程序，得到：

    ```python
    max_seq_len = t.seq_len_distribution(isplot=True)
    >>> print(max_seq_len)
    9
    ```

    ![seq_len_distribution2](https://s2.loli.net/2022/01/29/oryGCQupzHiMF37.png)

  - 修正后的频数分布图较好的反映了**微博评论长度服从右偏分布**，而此时取其峰值为`seq_len`较为合适，为9。

- `coding == "w"`

  - 同理，去除异常点，得到`seq_len = 6 `较为合适

    ```python
    max_seq_len = t.seq_len_distribution(isplot=True)
    >>> print(max_seq_len)
    6
    ```

    ![seq_len_distribution3.png](https://s2.loli.net/2022/01/29/ARDfbOa3hY82SLE.png)

### *5.5 Tokenizer在序列模型中的应用

- NLP问题中，文本都是离散化数据，故应将文本转化为数字；
- 很多问题中，词汇量巨大，但是可能大部分词都是低频词，对训练模型的贡献很小，反而会严重拖累模型的训练。所以，一般我们可以分析一下文本词汇的词频分布特征，选取词频占大头的一批词，可加快训练速度。

(Reference:  https://blog.csdn.net/keeppractice/article/details/106085242)
