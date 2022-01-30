## 第十一次作业 MapReduce——多进程

### 11.1 大致流程

- 将`news_sohusite_xml.smarty.dat`切分为若干个小文件，方便下列多进程的MapReduce过程；
- 建立Distributor进程，获取上述若干小文件的路径列表，负责将路径列表中的路径通过队列`file_queue = Queue()`传入某个Map进程中；
- 建立n个Map进程，接收`file_queue`中的路径，并读入文件进行`jieba`分词，并将分词结果传入另一个队列`result_queue = Queue()`；
- 建立Reduce进程，接收`result_queue = Queue()`中的结果，并进行汇总，将最终的汇总结果传入管道`summary_pipe = Pipe()`中；
- 最终`main`接收`summary_pipe[0]`中的结果，并将最终词频统计结果写入`txt`中；
- 编写装饰器，计算程序运行时间。

### 11.2 切分文档

```python
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
```

- 首先运行`get_line()`以获取`news_sohusite_xml.dat`的总行数，为8471976行；

- 注意到每六行为一个新闻，其格式如下，故共有$8471976/6=1411996$条新闻；

  ```html
  <doc>
  <url>页面URL</url>
  <docno>页面ID</docno>
  <contenttitle>页面标题</contenttitle>
  <content>页面内容</content>
  </doc>
  ```

- 故仅提取存在`"<content>"`字符串的行，并仅保留`<content></content>`之间的新闻评论；

- 约定一个文件存储10000条新闻；

- 最终得到了141个小的新闻文件。

<img src="https://s2.loli.net/2022/01/29/hSKZ2oTvUPGwIld.png" alt="image-20211210094053179" style="zoom: 40%;" />

### 11.3 MapReduce大致框架

```python
import os
import time
import jieba
from functools import wraps
from multiprocessing import Process, Queue, Pipe

abs_path = "D:/vscode py/现代程设/week 11/news/"

class Map(Process):
    '''
    Map进程读取文档并进行词频统计，返回该文本的词频统计结果。
    '''
    def __init__(self, i, fq, rq):
        super().__init__()

    def get_news(self):
        pass

    def read_news(self, news):
        pass

    def send_res(self, res, news):
        pass

    def run(self):
        pass

class Reduce(Process):
    '''
    Reduce进程收集所有Map进程提供的文档词频统计，更新总的文档库词频，
    并在所有map完成后保存总的词频到文件。
    '''
    def __init__(self, rq, sp, map_num):
        super().__init__()

    def recieve_result(self):
        pass

    def merge_result(self, data):
        pass

    def send_summary(self):
        pass

    def run(self):
        pass

class Distributor(Process):
    '''
    供多个Map进程竞争获取文档路径。
    '''
    def __init__(self, fq, map_num):
        super().__init__()

    def run(self):
        pass

def count_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pass
        return fun_res
    return wrapper

@count_time
def main():
    pass

if __name__ == "__main__":
    main()
```

### 11.4 Distributor类

```python
class Distributor(Process):
    '''
    供多个Map进程竞争获取文档路径。
    '''
    def __init__(self, fq, map_num):
        super().__init__()
        self.name = "Distributor"
        self.fq = fq
        self.map_num = map_num

    def run(self):
        for name in os.listdir(abs_path):
            f_path = os.path.join(abs_path, name)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
                  f": {self.name} puts {f_path} into fq.")
            self.fq.put(f_path)
        for _ in range(self.map_num):
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
                  f": {self.name} puts None into fq.")
            self.fq.put(None)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
              ": All file has been put.")
```

- 类中`run`方法将读取的路径逐一传入`file_queue`中；
- 均传入之后，将Map进程数个数的`None`传入`file_queue`中。

### 11.5 Map类

```python
class Map(Process):
    '''
    Map进程读取文档并进行词频统计，返回该文本的词频统计结果。
    '''
    def __init__(self, i, fq, rq):
        super().__init__()
        self.name = f"Map {i+1}"
        self.fq = fq
        self.rq = rq

    def get_news(self):
        path = self.fq.get()
        if path is None:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
                  f": {self.name} will close.")
            return
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
                  f": {self.name} gets {path} from fq.")
            return path

    def read_news(self, path):
        with open(path, "r", encoding="GB18030") as f:
            lines = f.read()
            words = jieba.lcut(lines)
        freq_dic = {}
        for word in words:
            freq_dic[word] = freq_dic.get(word, 0) + 1
        return freq_dic

    def send_result(self, res, path):
        self.rq.put(res)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
              f": {self.name} puts {path} result into rq.")

    def run(self):
        while True:
            path = self.get_news()
            if path is None:
                self.rq.put(None)
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
                      f": {self.name} puts None into rq")
                break
            else:
                res = self.read_news(path)
                self.send_result(res, path)
```

- 在`run`方法中调用`get_news`方法循环接收新闻，若接收值为`None`，则停止接收；若不为`None`，则调用`read_news`方法读取新闻文件且做分词处理，将返回的词频字典通过`send_result`方法传入`rq`中；
- 在`get_news`方法中，从`fq`中得到路径，若为`None`，则代表全部路径已读入；若不为`None`，则返回路径；
- 在`read_news`方法中，从得到的`path`读入新闻文件，并进行分词处理，将得到的词频字典返回；
- 在`send_result`方法中，将得到的词频字典传入`rq`中。

### 11.6 Reduce类

```python
class Reduce(Process):
    '''
    Reduce进程收集所有Map进程提供的文档词频统计，更新总的文档库词频，
    并在所有map完成后保存总的词频到文件。
    '''
    def __init__(self, rq, sp, map_num):
        super().__init__()
        self.name = "Reduce"
        self.rq = rq
        self.sp = sp[1]
        self.res_dic = {}
        self.cnt_none = 0
        self.map_num = map_num

    def recieve_result(self):
        data = self.rq.get()
        if data is None:
            self.cnt_none += 1
            if self.cnt_none == self.map_num:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
                      ": All process ends!")
                return None
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
                  f": {self.cnt_none} processes ends.")
            return 0
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
                  f": {self.name} gets one res from rq.")
            return data

    def merge_result(self, data):
        for key, value in data.items():
            self.res_dic[key] = self.res_dic.get(key, 0) + value

    def send_summary(self):
        self.sp.send(self.res_dic)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
              f": {self.name} puts summary result to pipe.")

    def run(self):
        while True:
            data = self.recieve_result()
            if data is None:
                break
            elif data == 0:
                continue
            else:
                self.merge_result(data)
        self.send_summary()
```

- 在`run`方法中，循环接收`rq`中传入的结果，若传入的`None`值数量等于Map进程数量，则代表结果已收齐，最终将已整合好的数据传入`sp`；
- 在`recieve_result`方法中，接收`rq`中传入的结果，并统计接收到的`None`数量，若等于Map进程数则代表结果已收齐，Reduce进程结束；若未达到进程数，则返回词频字典；
- 在`merge_result`方法中，将词频字典整合为一个字典；
- 在`send_summary`方法中，将已整合好的词频字典传入`sp`。

### 11.7 count_time装饰器

```python
def count_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        fun_res = func(*args, **kwargs)
        end = time.time()
        print(f"func {func.__name__} running time: {end-start} sec.")
        return fun_res
    return wrapper
```

- 计算程序运行时间

### 11.8 main函数

```python
@count_time
def main():
    # map_num = os.cpu_count()
    map_num = int(sys.argv[1])
    file_queue = Queue()
    result_queue = Queue()
    summary_pipe = Pipe()

    Dis = Distributor(file_queue, map_num)
    Dis.start()
    maps = []
    for i in range(map_num):
        M = Map(i, file_queue, result_queue)
        maps.append(M)
        M.start()
    R = Reduce(result_queue, summary_pipe, map_num)
    R.start()
    Dis.join()
    for map in maps:
        map.join()
    while True:
        res = summary_pipe[0].recv()
        res = sorted(res.items(), lambda x:x[1], reverse=True)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + 
              ": Main gets summary result through pipe.")
        break
    summary_pipe[0].close()
    summary_pipe[1].close()
    with open("MapReduceFrequency.txt", "w", encoding="GB18030") as f:
        f.write(str(res))
```

- 建立`map_num`个Map进程数；
- 将经降序排列的字典保存至`MapReduceFrequency.txt`中。

### 11.9 结果展示

#### 11.9.1 map_num = 2

```python
D:\vscode py\现代程设\week 11>python mapreduce.py 2
2021-12-10 12:30:16: Distributor puts D:/vscode py/现代程设/week 11/news/1.txt into fq.
2021-12-10 12:30:16: Distributor puts D:/vscode py/现代程设/week 11/news/10.txt into fq.
2021-12-10 12:30:16: Distributor puts D:/vscode py/现代程设/week 11/news/100.txt into fq.
2021-12-10 12:30:16: Map 1 gets D:/vscode py/现代程设/week 11/news/1.txt from fq.
2021-12-10 12:30:16: Distributor puts D:/vscode py/现代程设/week 11/news/101.txt into fq.
2021-12-10 12:30:16: Map 2 gets D:/vscode py/现代程设/week 11/news/10.txt from fq.
2021-12-10 12:30:16: Distributor puts D:/vscode py/现代程设/week 11/news/102.txt into fq.
...
2021-12-10 12:30:16: Distributor puts D:/vscode py/现代程设/week 11/news/99.txt into fq.
2021-12-10 12:30:16: Distributor puts None into fq.
2021-12-10 12:30:16: Distributor puts None into fq.
2021-12-10 12:30:16: All file has been put.
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Loading model cost 0.840 seconds.
Prefix dict has been built successfully.
Loading model cost 0.993 seconds.
Prefix dict has been built successfully.
2021-12-10 12:30:39: Map 1 puts D:/vscode py/现代程设/week 11/news/1.txt result into rq.
2021-12-10 12:30:39: Map 1 gets D:/vscode py/现代程设/week 11/news/100.txt from fq.
2021-12-10 12:30:39: Reduce gets one res from rq.
2021-12-10 12:30:41: Map 2 puts D:/vscode py/现代程设/week 11/news/10.txt result into rq.
2021-12-10 12:30:41: Map 2 gets D:/vscode py/现代程设/week 11/news/101.txt from fq.
2021-12-10 12:30:41: Reduce gets one res from rq.
2021-12-10 12:31:02: Map 1 puts D:/vscode py/现代程设/week 11/news/100.txt result into rq.
2021-12-10 12:31:02: Map 1 gets D:/vscode py/现代程设/week 11/news/102.txt from fq.
2021-12-10 12:31:02: Reduce gets one res from rq.
2021-12-10 12:31:06: Map 2 puts D:/vscode py/现代程设/week 11/news/101.txt result into rq.
2021-12-10 12:31:06: Map 2 gets D:/vscode py/现代程设/week 11/news/103.txt from fq.
2021-12-10 12:31:06: Reduce gets one res from rq.
...
2021-12-10 12:56:09: Map 2 puts D:/vscode py/现代程设/week 11/news/98.txt result into rq.
2021-12-10 12:56:09: Map 2 will close.
2021-12-10 12:56:09: Map 2 puts None into rq
2021-12-10 12:56:09: Reduce gets one res from rq.
2021-12-10 12:56:09: 1 processes ends.
2021-12-10 12:56:20: Map 1 puts D:/vscode py/现代程设/week 11/news/99.txt result into rq.
2021-12-10 12:56:20: Map 1 will close.
2021-12-10 12:56:20: Map 1 puts None into rq
2021-12-10 12:56:20: Reduce gets one res from rq.
2021-12-10 12:56:20: All process ends!
2021-12-10 12:56:21: Reduce puts summary result to pipe.
2021-12-10 12:56:21: Main gets summary result through pipe.
func main running time: 1567.5825431346893 sec.
```

- `func main running time: 1567.5825431346893 sec.`

#### 11.9.2 map_num = 4

```python
D:\vscode py\现代程设\week 11>python mapreduce.py 4
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/1.txt into fq.
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/10.txt into fq.
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/100.txt into fq.
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/101.txt into fq.
...
2021-12-10 08:48:24: Map 1 gets D:/vscode py/现代程设/week 11/news/1.txt from fq.
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/124.txt into fq.
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/125.txt into fq.
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/126.txt into fq.
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/127.txt into fq.
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/128.txt into fq.
...
2021-12-10 08:48:24: Distributor puts D:/vscode py/现代程设/week 11/news/99.txt into fq.
2021-12-10 08:48:24: Distributor puts None into fq.
2021-12-10 08:48:24: Distributor puts None into fq.
2021-12-10 08:48:24: Distributor puts None into fq.
2021-12-10 08:48:24: Distributor puts None into fq.
2021-12-10 08:48:24: All file has been put.
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Loading model cost 0.792 seconds.
Prefix dict has been built successfully.
Loading model cost 0.769 seconds.
Prefix dict has been built successfully.
Loading model cost 0.883 seconds.
Prefix dict has been built successfully.
Loading model cost 1.252 seconds.
Prefix dict has been built successfully.
2021-12-10 08:48:50: Map 3 puts D:/vscode py/现代程设/week 11/news/100.txt result into rq.
2021-12-10 08:48:50: Map 3 gets D:/vscode py/现代程设/week 11/news/102.txt from fq.
2021-12-10 08:48:50: Reduce gets one res from rq.
2021-12-10 08:48:50: Map 1 puts D:/vscode py/现代程设/week 11/news/1.txt result into rq.
2021-12-10 08:48:50: Map 1 gets D:/vscode py/现代程设/week 11/news/103.txt from fq.
2021-12-10 08:48:51: Reduce gets one res from rq.
2021-12-10 08:48:53: Map 4 puts D:/vscode py/现代程设/week 11/news/10.txt result into rq.
2021-12-10 08:48:53: Map 4 gets D:/vscode py/现代程设/week 11/news/104.txt from fq.
2021-12-10 08:48:53: Reduce gets one res from rq.
2021-12-10 08:48:54: Map 2 puts D:/vscode py/现代程设/week 11/news/101.txt result into rq.
2021-12-10 08:48:54: Map 2 gets D:/vscode py/现代程设/week 11/news/105.txt from fq.
2021-12-10 08:48:54: Reduce gets one res from rq.
...
2021-12-10 09:04:18: Map 4 puts D:/vscode py/现代程设/week 11/news/95.txt result into rq.
2021-12-10 09:04:18: Map 4 gets D:/vscode py/现代程设/week 11/news/99.txt from fq.
2021-12-10 09:04:18: Reduce gets one res from rq.
2021-12-10 09:04:29: Map 2 puts D:/vscode py/现代程设/week 11/news/96.txt result into rq.
2021-12-10 09:04:29: Map 2 will close.
2021-12-10 09:04:29: Map 2 puts None into rq
2021-12-10 09:04:29: Reduce gets one res from rq.
2021-12-10 09:04:29: 1 processes ends.
2021-12-10 09:04:31: Map 1 puts D:/vscode py/现代程设/week 11/news/97.txt result into rq.
2021-12-10 09:04:31: Map 1 will close.
2021-12-10 09:04:31: Map 1 puts None into rq
2021-12-10 09:04:31: Reduce gets one res from rq.
2021-12-10 09:04:31: 2 processes ends.
2021-12-10 09:04:34: Map 3 puts D:/vscode py/现代程设/week 11/news/98.txt result into rq.
2021-12-10 09:04:34: Map 3 will close.
2021-12-10 09:04:34: Map 3 puts None into rq
2021-12-10 09:04:34: Reduce gets one res from rq.
2021-12-10 09:04:34: 3 processes ends.
2021-12-10 09:04:42: Map 4 puts D:/vscode py/现代程设/week 11/news/99.txt result into rq.
2021-12-10 09:04:42: Map 4 will close.
2021-12-10 09:04:42: Map 4 puts None into rq
2021-12-10 09:04:42: Reduce gets one res from rq.
2021-12-10 09:04:42: All process ends!
2021-12-10 09:04:42: Reduce puts summary result to pipe.
2021-12-10 09:04:42: Main gets summary result through pipe.
func main running time: 980.169985294342 sec.
```

- `func main running time: 980.169985294342 sec.`

#### 11.9.3 map_num = 8

```python
D:\vscode py\现代程设\week 11>python mapreduce.py 8
2021-12-10 01:21:54: Distributor puts D:/vscode py/现代程设/week 11/news/1.txt into fq.
2021-12-10 01:21:54: Distributor puts D:/vscode py/现代程设/week 11/news/10.txt into fq.
2021-12-10 01:21:54: Distributor puts D:/vscode py/现代程设/week 11/news/100.txt into fq.
2021-12-10 01:21:54: Map 1 gets D:/vscode py/现代程设/week 11/news/1.txt from fq.
2021-12-10 01:21:54: Map 5 gets D:/vscode py/现代程设/week 11/news/10.txt from fq.
2021-12-10 01:21:54: Distributor puts D:/vscode py/现代程设/week 11/news/101.txt into fq.
2021-12-10 01:21:54: Distributor puts D:/vscode py/现代程设/week 11/news/102.txt into fq.
2021-12-10 01:21:54: Map 2 gets D:/vscode py/现代程设/week 11/news/100.txt from fq.
2021-12-10 01:21:54: Map 8 gets D:/vscode py/现代程设/week 11/news/101.txt from fq.
...
2021-12-10 01:21:54: Distributor puts D:/vscode py/现代程设/week 11/news/38.txt into fq.
2021-12-10 01:21:54: Map 6 gets D:/vscode py/现代程设/week 11/news/102.txt from fq.
2021-12-10 01:21:54: Map 3 gets D:/vscode py/现代程设/week 11/news/103.txt from fq.
2021-12-10 01:21:54: Map 4 gets D:/vscode py/现代程设/week 11/news/104.txt from fq.
2021-12-10 01:21:54: Map 7 gets D:/vscode py/现代程设/week 11/news/105.txt from fq.
...
2021-12-10 01:21:54: Distributor puts D:/vscode py/现代程设/week 11/news/98.txt into fq.
2021-12-10 01:21:54: Distributor puts D:/vscode py/现代程设/week 11/news/99.txt into fq.
2021-12-10 01:21:54: Distributor puts None into fq.
...
2021-12-10 01:21:54: Distributor puts None into fq.
2021-12-10 01:21:54: All file has been put.
...
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
...
Loading model cost 1.396 seconds.
Prefix dict has been built successfully.
2021-12-10 01:22:37: Map 6 puts D:/vscode py/现代程设/week 11/news/102.txt result into rq.
2021-12-10 01:22:37: Map 6 gets D:/vscode py/现代程设/week 11/news/106.txt from fq.
2021-12-10 01:22:37: Map 3 puts D:/vscode py/现代程设/week 11/news/103.txt result into rq.
2021-12-10 01:22:37: Reduce gets one res from rq.
2021-12-10 01:22:37: Map 3 gets D:/vscode py/现代程设/week 11/news/107.txt from fq.
2021-12-10 01:22:37: Reduce gets one res from rq.
2021-12-10 01:22:38: Map 7 puts D:/vscode py/现代程设/week 11/news/105.txt result into rq.
2021-12-10 01:22:38: Map 7 gets D:/vscode py/现代程设/week 11/news/108.txt from fq.
2021-12-10 01:22:38: Reduce gets one res from rq.
2021-12-10 01:22:40: Map 1 puts D:/vscode py/现代程设/week 11/news/1.txt result into rq.
2021-12-10 01:22:40: Map 2 puts D:/vscode py/现代程设/week 11/news/100.txt result into rq.
2021-12-10 01:22:40: Map 1 gets D:/vscode py/现代程设/week 11/news/109.txt from fq.
2021-12-10 01:22:40: Map 2 gets D:/vscode py/现代程设/week 11/news/11.txt from fq.
2021-12-10 01:22:40: Reduce gets one res from rq.
2021-12-10 01:22:40: Reduce gets one res from rq.
2021-12-10 01:22:42: Map 4 puts D:/vscode py/现代程设/week 11/news/104.txt result into rq.
2021-12-10 01:22:42: Map 4 gets D:/vscode py/现代程设/week 11/news/110.txt from fq.
2021-12-10 01:22:43: Reduce gets one res from rq.
2021-12-10 01:22:44: Map 5 puts D:/vscode py/现代程设/week 11/news/10.txt result into rq.
2021-12-10 01:22:44: Map 5 gets D:/vscode py/现代程设/week 11/news/111.txt from fq.
2021-12-10 01:22:44: Reduce gets one res from rq.
2021-12-10 01:22:44: Map 8 puts D:/vscode py/现代程设/week 11/news/101.txt result into rq.
2021-12-10 01:22:45: Map 8 gets D:/vscode py/现代程设/week 11/news/112.txt from fq.
...
2021-12-10 01:36:00: Map 5 puts D:/vscode py/现代程设/week 11/news/91.txt result into rq.
2021-12-10 01:36:00: Map 5 gets D:/vscode py/现代程设/week 11/news/99.txt from fq.
2021-12-10 01:36:00: Reduce gets one res from rq.
2021-12-10 01:36:11: Map 3 puts D:/vscode py/现代程设/week 11/news/92.txt result into rq.
2021-12-10 01:36:11: Map 3 will close.
2021-12-10 01:36:11: Map 3 puts None into rq
2021-12-10 01:36:11: Reduce gets one res from rq.
2021-12-10 01:36:11: 1 processes ends.
...
2021-12-10 01:36:30: 6 processes ends.
2021-12-10 01:36:32: Map 2 puts D:/vscode py/现代程设/week 11/news/98.txt result into rq.
2021-12-10 01:36:32: Map 2 will close.
2021-12-10 01:36:32: Map 2 puts None into rq
2021-12-10 01:36:32: Reduce gets one res from rq.
2021-12-10 01:36:32: 7 processes ends.
2021-12-10 01:36:36: Map 5 puts D:/vscode py/现代程设/week 11/news/99.txt result into rq.
2021-12-10 01:36:36: Map 5 will close.
2021-12-10 01:36:36: Map 5 puts None into rq
2021-12-10 01:36:36: Reduce gets one res from rq.
2021-12-10 01:36:36: All process ends!
2021-12-10 01:36:37: Reduce puts summary result to pipe.
2021-12-10 01:36:37: Main gets summary result through pipe.
func main running time: 885.2300641536713 sec.
```

- `func main running time: 885.2300641536713 sec.`

#### 11.9.4 map_num = 16

```python
D:\vscode py\现代程设\week 11>python mapreduce.py 16
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/1.txt into fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/10.txt into fq.
2021-12-10 01:38:44: Map 9 gets D:/vscode py/现代程设/week 11/news/1.txt from fq.
2021-12-10 01:38:44: Map 7 gets D:/vscode py/现代程设/week 11/news/10.txt from fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/100.txt into fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/101.txt into fq.
2021-12-10 01:38:44: Map 5 gets D:/vscode py/现代程设/week 11/news/100.txt from fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/102.txt into fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/103.txt into fq.
2021-12-10 01:38:44: Map 2 gets D:/vscode py/现代程设/week 11/news/101.txt from fq.
2021-12-10 01:38:44: Map 13 gets D:/vscode py/现代程设/week 11/news/102.txt from fq.
2021-12-10 01:38:44: Map 12 gets D:/vscode py/现代程设/week 11/news/103.txt from fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/104.txt into fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/105.txt into fq.
2021-12-10 01:38:44: Map 10 gets D:/vscode py/现代程设/week 11/news/104.txt from fq.
2021-12-10 01:38:44: Map 15 gets D:/vscode py/现代程设/week 11/news/105.txt from fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/106.txt into fq.
2021-12-10 01:38:44: Distributor puts D:/vscode py/现代程设/week 11/news/107.txt into fq.
2021-12-10 01:38:44: Map 11 gets D:/vscode py/现代程设/week 11/news/106.txt from fq.
...
2021-12-10 01:38:45: Map 16 gets D:/vscode py/现代程设/week 11/news/110.txt from fq.
2021-12-10 01:38:45: Distributor puts D:/vscode py/现代程设/week 11/news/37.txt into fq.
...
2021-12-10 01:38:45: Distributor puts None into fq.
2021-12-10 01:38:45: All file has been put.
...
Loading model cost 4.932 seconds.
Prefix dict has been built successfully.
2021-12-10 01:39:35: Map 9 puts D:/vscode py/现代程设/week 11/news/1.txt result into rq.
2021-12-10 01:39:36: Map 9 gets D:/vscode py/现代程设/week 11/news/113.txt from fq.
2021-12-10 01:39:36: Reduce gets one res from rq.
2021-12-10 01:39:52: Map 2 puts D:/vscode py/现代程设/week 11/news/101.txt result into rq.
2021-12-10 01:39:52: Map 2 gets D:/vscode py/现代程设/week 11/news/114.txt from fq.
2021-12-10 01:39:52: Reduce gets one res from rq.
2021-12-10 01:40:00: Map 12 puts D:/vscode py/现代程设/week 11/news/103.txt result into rq.
2021-12-10 01:40:01: Map 12 gets D:/vscode py/现代程设/week 11/news/115.txt from fq.
2021-12-10 01:40:01: Reduce gets one res from rq.
...
2021-12-10 01:56:17: Map 13 puts D:/vscode py/现代程设/week 11/news/89.txt result into rq.
2021-12-10 01:56:17: Map 13 gets D:/vscode py/现代程设/week 11/news/99.txt from fq.
2021-12-10 01:56:18: Reduce gets one res from rq.
2021-12-10 01:56:24: Map 15 puts D:/vscode py/现代程设/week 11/news/77.txt result into rq.
2021-12-10 01:56:25: Map 15 will close.
2021-12-10 01:56:25: Map 15 puts None into rq
2021-12-10 01:56:25: Reduce gets one res from rq.
2021-12-10 01:56:25: 1 processes ends.
...
2021-12-10 01:57:02: Map 1 puts D:/vscode py/现代程设/week 11/news/9.txt result into rq.
2021-12-10 01:57:03: Map 1 will close.
2021-12-10 01:57:03: Map 1 puts None into rq
2021-12-10 01:57:03: Reduce gets one res from rq.
2021-12-10 01:57:03: 11 processes ends.
2021-12-10 01:57:07: Map 16 puts D:/vscode py/现代程设/week 11/news/95.txt result into rq.
2021-12-10 01:57:07: Map 16 will close.
2021-12-10 01:57:07: Map 16 puts None into rq
2021-12-10 01:57:08: Reduce gets one res from rq.
2021-12-10 01:57:08: 12 processes ends.
2021-12-10 01:57:13: Map 7 puts D:/vscode py/现代程设/week 11/news/98.txt result into rq.
2021-12-10 01:57:13: Map 7 will close.
2021-12-10 01:57:13: Map 7 puts None into rq
2021-12-10 01:57:13: Reduce gets one res from rq.
2021-12-10 01:57:14: 13 processes ends.
2021-12-10 01:57:19: Map 3 puts D:/vscode py/现代程设/week 11/news/97.txt result into rq.
2021-12-10 01:57:19: Map 3 will close.
2021-12-10 01:57:19: Map 3 puts None into rq
2021-12-10 01:57:19: Reduce gets one res from rq.
2021-12-10 01:57:19: 14 processes ends.
2021-12-10 01:57:21: Map 13 puts D:/vscode py/现代程设/week 11/news/99.txt result into rq.
2021-12-10 01:57:21: Map 13 will close.
2021-12-10 01:57:21: Map 13 puts None into rq
2021-12-10 01:57:21: Reduce gets one res from rq.
2021-12-10 01:57:21: 15 processes ends.
2021-12-10 01:57:23: Map 4 puts D:/vscode py/现代程设/week 11/news/96.txt result into rq.
2021-12-10 01:57:23: Map 4 will close.
2021-12-10 01:57:23: Map 4 puts None into rq
2021-12-10 01:57:23: Reduce gets one res from rq.
2021-12-10 01:57:23: All process ends!
2021-12-10 01:57:23: Reduce puts summary result to pipe.
2021-12-10 01:57:24: Main gets summary result through pipe.
func main running time: 1123.0413343906403 sec.
```

- `func main running time: 1123.0413343906403 sec.`

#### 11.9.5 map_num = 24

```python
D:\vscode py\现代程设\week 11>python mapreduce.py 24
2021-12-10 12:57:37: Distributor puts D:/vscode py/现代程设/week 11/news/1.txt into fq.
2021-12-10 12:57:37: Distributor puts D:/vscode py/现代程设/week 11/news/10.txt into fq.
2021-12-10 12:57:37: Distributor puts D:/vscode py/现代程设/week 11/news/100.txt into fq.
2021-12-10 12:57:37: Map 22 gets D:/vscode py/现代程设/week 11/news/1.txt from fq.
2021-12-10 12:57:37: Map 8 gets D:/vscode py/现代程设/week 11/news/10.txt from fq.
2021-12-10 12:57:37: Map 15 gets D:/vscode py/现代程设/week 11/news/100.txt from fq.
2021-12-10 12:57:37: Distributor puts D:/vscode py/现代程设/week 11/news/101.txt into fq.
2021-12-10 12:57:37: Map 3 gets D:/vscode py/现代程设/week 11/news/101.txt from fq.
...
2021-12-10 12:57:39: Distributor puts None into fq.
2021-12-10 12:57:39: Distributor puts None into fq.
2021-12-10 12:57:39: All file has been put.
..
Prefix dict has been built successfully.
Loading model cost 7.272 seconds.
Prefix dict has been built successfully.
Loading model cost 15.326 seconds.
Prefix dict has been built successfully.
Loading model cost 16.225 seconds.
Prefix dict has been built successfully.
2021-12-10 12:58:50: Map 21 puts D:/vscode py/现代程设/week 11/news/111.txt result into rq.
2021-12-10 12:58:50: Map 21 gets D:/vscode py/现代程设/week 11/news/120.txt from fq.
2021-12-10 12:58:50: Reduce gets one res from rq.
2021-12-10 12:59:53: Map 24 puts D:/vscode py/现代程设/week 11/news/113.txt result into rq.
2021-12-10 12:59:54: Map 24 gets D:/vscode py/现代程设/week 11/news/121.txt from fq.
2021-12-10 12:59:54: Reduce gets one res from rq.
2021-12-10 13:00:32: Map 21 puts D:/vscode py/现代程设/week 11/news/120.txt result into rq.
2021-12-10 13:00:33: Map 21 gets D:/vscode py/现代程设/week 11/news/122.txt from fq.
2021-12-10 13:00:33: Reduce gets one res from rq.
2021-12-10 13:00:37: Map 1 puts D:/vscode py/现代程设/week 11/news/102.txt result into rq.
2021-12-10 13:00:37: Map 1 gets D:/vscode py/现代程设/week 11/news/123.txt from fq.
2021-12-10 13:00:37: Reduce gets one res from rq.
...
2021-12-10 13:24:45: Map 19 puts D:/vscode py/现代程设/week 11/news/79.txt result into rq.
2021-12-10 13:24:45: Map 19 gets D:/vscode py/现代程设/week 11/news/99.txt from fq.
2021-12-10 13:24:45: Reduce gets one res from rq.
2021-12-10 13:24:50: Map 3 puts D:/vscode py/现代程设/week 11/news/80.txt result into rq.
2021-12-10 13:24:50: Map 3 will close.
2021-12-10 13:24:50: Map 3 puts None into rq
2021-12-10 13:24:51: Reduce gets one res from rq.
2021-12-10 13:24:51: 1 processes ends.
2021-12-10 13:25:04: Map 9 puts D:/vscode py/现代程设/week 11/news/69.txt result into rq.
2021-12-10 13:25:04: Map 9 will close.
2021-12-10 13:25:04: Map 9 puts None into rq
2021-12-10 13:25:05: Reduce gets one res from rq.
2021-12-10 13:25:05: 2 processes ends.
...
2021-12-10 13:26:44: 19 processes ends.
2021-12-10 13:26:45: Map 11 puts D:/vscode py/现代程设/week 11/news/93.txt result into rq.
2021-12-10 13:26:46: Map 11 will close.
2021-12-10 13:26:46: Map 11 puts None into rq
2021-12-10 13:26:46: Reduce gets one res from rq.
2021-12-10 13:26:46: 20 processes ends.
2021-12-10 13:26:46: Map 17 puts D:/vscode py/现代程设/week 11/news/95.txt result into rq.
2021-12-10 13:26:46: Map 17 will close.
2021-12-10 13:26:46: Map 17 puts None into rq
2021-12-10 13:26:46: Reduce gets one res from rq.
2021-12-10 13:26:46: 21 processes ends.
2021-12-10 13:26:49: Map 21 puts D:/vscode py/现代程设/week 11/news/98.txt result into rq.
2021-12-10 13:26:49: Map 21 will close.
2021-12-10 13:26:49: Map 21 puts None into rq
2021-12-10 13:26:49: Reduce gets one res from rq.
2021-12-10 13:26:49: 22 processes ends.
2021-12-10 13:26:50: Map 13 puts D:/vscode py/现代程设/week 11/news/96.txt result into rq.
2021-12-10 13:26:50: Map 13 will close.
2021-12-10 13:26:50: Map 13 puts None into rq
2021-12-10 13:26:50: Reduce gets one res from rq.
2021-12-10 13:26:50: 23 processes ends.
2021-12-10 13:27:00: Map 19 puts D:/vscode py/现代程设/week 11/news/99.txt result into rq.
2021-12-10 13:27:00: Map 19 will close.
2021-12-10 13:27:00: Map 19 puts None into rq
2021-12-10 13:27:00: Reduce gets one res from rq.
2021-12-10 13:27:00: All process ends!
2021-12-10 13:27:01: Reduce puts summary result to pipe.
2021-12-10 13:27:01: Main gets summary result through pipe.
func main running time: 1771.3666546344757 sec.
```

- `func main running time: 1771.3666546344757 sec.`

#### 11.9.6 map_num = 32

```python
D:\vscode py\现代程设\week 11>python mapreduce.py 32
2021-12-10 01:59:05: Distributor puts D:/vscode py/现代程设/week 11/news/1.txt into fq.
...
2021-12-10 01:59:06: Distributor puts D:/vscode py/现代程设/week 11/news/114.txt into fq.
2021-12-10 01:59:06: Map 19 gets D:/vscode py/现代程设/week 11/news/1.txt from fq.
2021-12-10 01:59:06: Distributor puts D:/vscode py/现代程设/week 11/news/115.txt into fq.
2021-12-10 01:59:06: Distributor puts D:/vscode py/现代程设/week 11/news/116.txt into fq.
2021-12-10 01:59:06: Distributor puts D:/vscode py/现代程设/week 11/news/117.txt into fq.
2021-12-10 01:59:06: Distributor puts D:/vscode py/现代程设/week 11/news/118.txt into fq.
...
2021-12-10 01:59:07: Map 30 gets D:/vscode py/现代程设/week 11/news/103.txt from fq.
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
2021-12-10 01:59:07: Map 22 gets D:/vscode py/现代程设/week 11/news/104.txt from fq.
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Building prefix dict from the default dictionary ...
2021-12-10 01:59:07: Distributor puts D:/vscode py/现代程设/week 11/news/130.txt into fq.
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
2021-12-10 01:59:07: Distributor puts D:/vscode py/现代程设/week 11/news/131.txt into fq.
2021-12-10 01:59:07: Map 25 gets D:/vscode py/现代程设/week 11/news/105.txt from fq.
2021-12-10 01:59:07: Distributor puts D:/vscode py/现代程设/week 11/news/132.txt into fq.
...
2021-12-10 01:59:08: Map 7 gets D:/vscode py/现代程设/week 11/news/109.txt from fq.
2021-12-10 01:59:08: Distributor puts D:/vscode py/现代程设/week 11/news/16.txt into fq.
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
2021-12-10 01:59:08: Distributor puts D:/vscode py/现代程设/week 11/news/17.txt into fq.
2021-12-10 01:59:08: Distributor puts D:/vscode py/现代程设/week 11/news/18.txt into fq.
2021-12-10 01:59:08: Distributor puts D:/vscode py/现代程设/week 11/news/19.txt into fq.
...
Building prefix dict from the default dictionary ...
2021-12-10 01:59:08: Map 27 gets D:/vscode py/现代程设/week 11/news/111.txt from fq.
...
2021-12-10 01:59:12: Distributor puts D:/vscode py/现代程设/week 11/news/43.txt into fq.
Building prefix dict from the default dictionary ...
2021-12-10 01:59:13: Map 26 gets D:/vscode py/现代程设/week 11/news/126.txt from fq.
2021-12-10 01:59:14: Map 14 gets D:/vscode py/现代程设/week 11/news/127.txt from fq.
Building prefix dict from the default dictionary ...
Prefix dict has been built successfully.
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
2021-12-10 01:59:13: Distributor puts D:/vscode py/现代程设/week 11/news/44.txt into fq.
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
...
2021-12-10 01:59:17: Distributor puts D:/vscode py/现代程设/week 11/news/55.txt into fq.
Building prefix dict from the default dictionary ...
Building prefix dict from the default dictionary ...
Building prefix dict from the default dictionary ...
Building prefix dict from the default dictionary ...
Loading model cost 7.808 seconds.
2021-12-10 01:59:17: Distributor puts D:/vscode py/现代程设/week 11/news/56.txt into fq.
2021-12-10 01:59:18: Distributor puts D:/vscode py/现代程设/week 11/news/57.txt into fq.
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
2021-12-10 01:59:18: Distributor puts D:/vscode py/现代程设/week 11/news/58.txt into fq.
Building prefix dict from the default dictionary ...
...
Building prefix dict from the default dictionary ...
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Building prefix dict from the default dictionary ...
...
Loading model cost 14.025 seconds.
Building prefix dict from the default dictionary ...
Loading model cost 15.623 seconds.
Prefix dict has been built successfully.
2021-12-10 01:59:24: Distributor puts D:/vscode py/现代程设/week 11/news/74.txt into fq.
...
2021-12-10 01:59:29: Distributor puts D:/vscode py/现代程设/week 11/news/99.txt into fq.
...
2021-12-10 01:59:32: Distributor puts None into fq.
2021-12-10 01:59:33: Distributor puts None into fq.
2021-12-10 01:59:33: All file has been put.
...
Loading model cost 10.790 seconds.
Prefix dict has been built successfully.
Loading model from cache C:\Users\Liu_K\AppData\Local\Temp\jieba.cache
Loading model cost 31.955 seconds.
Prefix dict has been built successfully.
2021-12-10 02:00:47: Map 9 puts D:/vscode py/现代程设/week 11/news/115.txt result into rq.
2021-12-10 02:00:47: Map 9 gets D:/vscode py/现代程设/week 11/news/128.txt from fq.
2021-12-10 02:00:47: Reduce gets one res from rq.
2021-12-10 02:00:50: Map 10 puts D:/vscode py/现代程设/week 11/news/122.txt result into rq.
2021-12-10 02:00:51: Map 10 gets D:/vscode py/现代程设/week 11/news/129.txt from fq.
2021-12-10 02:00:51: Reduce gets one res from rq.
2021-12-10 02:02:47: Map 14 puts D:/vscode py/现代程设/week 11/news/127.txt result into rq.
2021-12-10 02:02:47: Map 14 gets D:/vscode py/现代程设/week 11/news/13.txt from fq.
2021-12-10 02:02:47: Reduce gets one res from rq.
2021-12-10 02:03:07: Map 29 puts D:/vscode py/现代程设/week 11/news/108.txt result into rq.
2021-12-10 02:03:07: Map 29 gets D:/vscode py/现代程设/week 11/news/130.txt from fq.
2021-12-10 02:03:07: Reduce gets one res from rq.
...
2021-12-10 02:04:53: Map 24 puts D:/vscode py/现代程设/week 11/news/117.txt result into rq.
2021-12-10 02:04:53: Map 32 puts D:/vscode py/现代程设/week 11/news/112.txt result into rq.
2021-12-10 02:04:54: Map 32 gets D:/vscode py/现代程设/week 11/news/24.txt from fq.
2021-12-10 02:04:54: Reduce gets one res from rq.
...
2021-12-10 02:28:06: Map 3 puts D:/vscode py/现代程设/week 11/news/73.txt result into rq.
2021-12-10 02:28:06: Map 3 will close.
2021-12-10 02:28:06: Map 3 puts None into rq
2021-12-10 02:28:06: 11 processes ends.
2021-12-10 02:28:06: Map 28 puts D:/vscode py/现代程设/week 11/news/91.txt result into rq.
2021-12-10 02:28:06: Map 28 will close.
2021-12-10 02:28:06: Map 28 puts None into rq
2021-12-10 02:28:06: Reduce gets one res from rq.
2021-12-10 02:28:07: Reduce gets one res from rq.
2021-12-10 02:28:07: Reduce gets one res from rq.
2021-12-10 02:28:07: Map 27 puts D:/vscode py/现代程设/week 11/news/80.txt result into rq.
2021-12-10 02:28:07: Map 27 will close.
2021-12-10 02:28:07: Map 27 puts None into rq
2021-12-10 02:28:07: 12 processes ends.
2021-12-10 02:28:08: Reduce gets one res from rq.
2021-12-10 02:28:08: 13 processes ends.
2021-12-10 02:28:08: 14 processes ends.
2021-12-10 02:28:08: Reduce gets one res from rq.
2021-12-10 02:28:08: Map 2 puts D:/vscode py/现代程设/week 11/news/8.txt result into rq.
2021-12-10 02:28:08: 15 processes ends.
2021-12-10 02:28:08: 16 processes ends.
2021-12-10 02:28:09: Map 2 will close.
...
2021-12-10 02:28:32: Map 8 will close.
2021-12-10 02:28:32: Map 8 puts None into rq
2021-12-10 02:28:32: Reduce gets one res from rq.
2021-12-10 02:28:32: 30 processes ends.
2021-12-10 02:28:34: Map 13 puts D:/vscode py/现代程设/week 11/news/98.txt result into rq.
2021-12-10 02:28:34: Map 13 will close.
2021-12-10 02:28:34: Map 13 puts None into rq
2021-12-10 02:28:34: Reduce gets one res from rq.
2021-12-10 02:28:34: 31 processes ends.
2021-12-10 02:28:36: Map 14 puts D:/vscode py/现代程设/week 11/news/99.txt result into rq.
2021-12-10 02:28:36: Map 14 will close.
2021-12-10 02:28:36: Map 14 puts None into rq
2021-12-10 02:28:36: Reduce gets one res from rq.
2021-12-10 02:28:36: All process ends!
2021-12-10 02:28:37: Reduce puts summary result to pipe.
2021-12-10 02:28:37: Main gets summary result through pipe.
func main running time: 2019.179684638977 sec.
```

- `func main running time: 2019.179684638977 sec.`
- （乱七八糟的多进程）

#### 11.9.7 进程数——时间折线图

<img src="https://s2.loli.net/2022/01/29/VbkNLvafcPW4nsd.png" alt="time" style="zoom:10%;" />

#### 11.9.8 最终词频统计结果

- `MapReduceFrequency.txt`

```python
[('，', 23103386), ('的', 13127131), ('\ue40c', 10802289), ('。', 9906869), ('\u3000', 8199669), ('０', 7932811), ('：', 6021770), ('１', 5847377), ('２', 5055751), ('、', 4231493), ('在', 3288789), ('了', 2823190), ('５', 2820470), ('３', 2773022), ('“', 2727825), ('”', 2722408), ('６', 2438177), ('４', 2222618), ('７', 2057207), ('是', 2033757), ('．', 2005769), ('和', 1945939), ('８', 1883647), ('（', 1832621), ('）', 1830747), ('９', 1543429), ('\n', 1410000), ('月', 1279747), ('也', 1104965), ('有', 1083085), ('为', 1069257), ('－', 1063498), ('将', 1003962), ('日', 1000578), ('Ｍ', 986020), ('ｅ', 948711), ('Ｃ', 939137), ('Ｐ', 934065), ('年', 927994), ('Ｇ', 895918), ('等', 872035), ('％', 850103), ('对', 829224), ('中', 810912), ('Ａ', 798297), ('与', 797047), ('Ｉ', 795003), ('ｎ', 787809), ('ｏ', 784348), ('ｉ', 776934), ('上', 776823), ('／', 769787), ('Ｂ', 741983), ('Ｓ', 721550), ('都', 717624), ('他', 712869), ('Ｕ', 709655), ('ｍ', 696779), ('不', 695857), ('到', 672477), ('就', 670983), ('Ｄ', 666554), ('记者', 641704), ('后', 618878), ('多', 604367), ('中国', 599347), ('》', 597347), ('《', 596796), ('我', 586135), ('；', 568627), ('更', 565176), ('＞', 556693), ('人', 554480), ('但', 547754), ('说', 545473), ('ｔ', 537981), ('系列', 528809), ('被', 517983), ('而', 509765), ('元', 507525), ('从', 504855), ('公司', 502385), ('并', 491878), ('这', 490027), ('ｌ', 480052), ('Ｈ', 479647), ('Ｔ', 479009), ('产品', 477517), ('ｒ', 469093), ('个', 468814), ('ａ', 453850), ('市场', 453115), ('时', 449229), ('一个', 448993), ('还', 445784), ('ｓ', 432623), ('会', 415001), ('要', 403284), ('我们', 392120), ('表示', 391116), ('以', 388894), ('没有', 387346), ('进行', 376756), ('Ｖ', 371715), ('ｄ', 359939), ('？', 356692), ('发展', 350875), ('让', 344347), ('自己', 334939), ('她', 326262), ('目前', 324641), ('工作', 321007), ('已经', 318785), ('企业', 318421), ('可以', 317650), ('华硕', 312969), ('尺寸', 309319), ('Ｌ', 309165), ('经济', 309112), ('英寸', 307097), ('情况', 299336), ('可', 298867), ('前', 296198), ('ｚ', 294538), ('很', 291500), ('屏幕', 286254), ('下', 285856), ('着', 285782), ('大', 284915), ('ｃ', 284224), ('Ｗ', 284056), ('据', 281202), ('参数', 281122), ('问题', 280642), ('及', 279733), ('已', 277655), ('Ｎ', 275228), ('Ｅ', 271912), ('他们', 270799), ('主频', 270794), ('其', 267569), ('新', 266139), ('于', 263883), ('北京', 262969), ('芯片', 262866), ('投资', 260568), ('硬盘容量', 259153), ('内存容量', 258838), ('时间', 257962), ('今年', 257309), ('显卡', 256423), ('地', 249371), ('来', 245659), ('能', 245468), ('向', 243215), ('Ｘ', 242019), ('Ｆ', 240596), ('美国', 239162), ('通过', 237052), ('给', 236001), ('座椅', 230562), ('或', 230518), ('可能', 230150), ('价格', 229160), ('型号', 226913), ('又', 226569), ('内', 226398), ('该', 225634), ('你', 224439), ('！', 224376), ('ｇ', 220863), ('同时', 220524), ('出现', 219346), ('开始', 217664), ('ｗ', 217511), ('操作系统', 216922), ('其中', 214753), ('基金', 214676), ('Ｏ', 214568), ('好', 214083), ('由', 211524), ('把', 206663), ('根据', 206333), ('国家', 205413), ('这个', 204431), ('认为', 204291), ('相关', 203675), ('＂', 202788), ('增长', 202180), ('系统', 201130), ('成为', 200854), ('服务', 199470), ('主要', 196826), ('活动', 196411), ('Ｒ', 195237), ('万元', 193895), ('方面', 193113), ('高', 192726), ('就是', 192003), ('亿元', 191843), ('称', 191585), ('最', 190917), ('项目', 190655), ('一', 189594), ('显示', 188559), ('如果', 188245), ('至', 187927), ('最大', 186951), ('比赛', 186701), ('汽车', 184566), ('以及', 183242), ('ｈ', 181393), ('发现', 180324), ('一些', 178959), ('政策', 178772), ('建设', 178319), ('信息', 175269), ('对于', 174326), ('影响', 173929), ('支持', 173604), ('报道', 173088), ('·', 172122), ('做', 170596), ('比', 167971), ('国际', 166999), ('提供', 166585), ('由于', 165600), ('去', 165492), ('现在', 165046), ('因为', 164796), ('ｋ', 162626), ('需要', 162100), ('方式', 162045), ('银行', 161138), ('作为', 160745), ('ｐ', 160444), ('要求', 160359), ('管理', 160089), ('这些', 159778), ('还是', 158088), ('调节', 157930), ('了解', 157915), ('里', 157684), ('却', 157463), ('安全', 157284), ('类型', 155807), ('分', 155190), ('城市', 154554), ('用', 152741), ('则', 151385), ('点', 150924), ('们', 150182), ('这样', 148237), ('小', 147994), ('…', 146932), ('ｕ', 146910), ('政府', 144986), ('岁', 143598), ('发生', 142644), ('其他', 141650), ('继续', 141361), ('孩子', 140688), ('包括', 140366), ('全国', 139863), ('但是', 139434), ('数据', 138969), ('过', 138391), ('资金', 137995), ('看', 137401), ('】', 137153), ('较', 137146), ('昨日', 136849), ('再', 135812), ('酷睿', 135722), ('【', 135225), ('进入', 134313), ('行业', 133697), ('现场', 133210), ('很多', 133032), ('名', 133014), ('销售', 132990), ('社会', 132950), ('发动机', 132500), ('使用', 132456), ('重要', 131577), ('超过', 131175), ('所', 130990), ('有限公司', 130878), ('车', 130673), ('达到', 130076), ('电动', 129494), ('之后', 129243), ('消息', 129214), ('不是', 129156), ('介绍', 127571), ('以上', 127477), ('部分', 127381), ('一直', 126732), ('号', 126166), ('实现', 126134), ('技术', 125533), ('不过', 125305), ('虽然', 124106), ('国内', 123459), ('出', 123374), ('自', 123281), ('中心', 122939), ('非常', 122540), ('上海', 122078), ('日电', 121755), ('万', 121534), ('部门', 120812), ('希望', 120797), ('生活', 120373), ('均', 120360), ('股', 120064), ('人员', 120009), ('搜狐', 119969), ('得', 119086), ('品牌', 119006), ('实际', 118537), ('仍', 118266), ('正在', 118055), ('关注', 117711), ('增加', 117569), ('地区', 117550), ('发布', 116865), ('获得', 115681), ('只', 114405), ('计划', 113981), ('机构', 113515), ('左右', 113093), ('世界', 113005), ('标准', 112820), ('参加', 112114), ('看到', 112080), ('以来', 111905), ('—', 111852), ('有关', 111776), ('还有', 111712), ('达', 111319), ('规定', 110847), ('合作', 110364), ('生产', 110037), ('家', 109924), ('近日', 109710), ('才', 109481), ('第', 109211), ('车辆', 108728), ('不能', 108531), ('进一步', 107997), ('基本', 107824), ('ｙ', 107636), ('因此', 107467), ('为了', 107414), ('约', 107114), ('ｂ', 107079), ('选择', 106850), ('去年', 106769), ('一次', 105240), ('集团', 104738), ('分别', 104405), ('表现', 104379), ('这种', 104339), ('一定', 104320), ('文化', 104206), ('下降', 103871), ('它', 103842), ('占', 103103), ('公布', 102289), ('媒体', 102107), ('学生', 102024), ('完成', 101728), ('时候', 101488), ('后排', 101445), ('我国', 101050), ('持续', 100341), ('举行', 100227), ('日本', 100114), ('未来', 99727), ('不少', 99637), ('结果', 99262), ('奥运会', 99216), ('此次', 99190), ('不会', 99124), ('月份', 98679), ('想', 98579), ('ｘ', 98520), ('全球', 98493), ('什么', 98287), ('因', 97986), ('过程', 97544), ('接受', 97363), ('同比', 97350), ('最高', 97323), ('不同', 97198), ('实施', 97151), ('证券', 96904), ('业务', 96727), ('伦敦', 96713), ('地方', 96345), ('各', 95887), ('之', 95706), ('两个', 95684), ('车型', 95659), ('调查', 95535), ('网友', 95531), ('研究', 95492), ('曾', 95174), ('设计', 94687), ('组织', 94090), ('告诉', 93392), ('能力', 93089), ('比较', 93036), ('所有', 92950), ('功能', 92871), ('投资者', 92750), ('提高', 92696), ('造成', 92278), ('所以', 92248), ('结构', 91959), ('没', 91673), ('报告', 91499), ('Ｋ', 91338), ('米', 91329), ('预计', 90953), ('当地', 90919), ('大家', 90651), ('自动', 90568), ('配置', 90414), ('存在', 90287), ('甚至', 89684), ('暂无', 89659), ('控制', 89614), ('需求', 89553), ('特别', 89387), ('小时', 88869), ('市民', 88536), ('而且', 88399), ('当', 88366), ('股份', 88342), ('消费者', 88334), ('明显', 87931), ('原因', 87788), ('这是', 87758), ('得到', 87698), ('方向盘', 87568), ('Ｑ', 87567), ('一名', 87296), ('双核', 87175), ('能够', 86878), ('风险', 86862), ('单位', 86545), ('近', 86483), ('正式', 86094), ('调整', 85994), ('使', 85901), ('最终', 85447), ('分析', 85417), ('应该', 85411), ('最后', 85236), ('是否', 85189), ('导致', 84911), ('不断', 84760), ('带来', 84593), ('上涨', 84408), ('一起', 84264), ('推出', 84241), ('香港', 84155), ('手机', 83998), ('只有', 83962), ('路', 83825), ('上半年', 83497), ('来自', 83236), ('讯', 83118), ('医院', 82896), ('学校', 82411), ('款', 82202), ('会议', 82009), ('随着', 81976), ('经销商', 81971), ('按照', 81948), ('您', 81739), ('网络', 81366), ('交易', 81251), ('指出', 81216), ('市', 80787), ('经过', 80774), ('直接', 80738), ('购买', 80656), ('上市', 80613), ('综合', 80595), ('环境', 80584), ('决定', 80161), ('专业', 80147), ('昨天', 80110), ('代表', 79952), ('收入', 79930), ('利率', 79907), ('走', 79825), ('以下', 79799), ('公告', 79391), ('关于', 79281), ('广州', 79160), ('开展', 79099), ('一位', 79093), ('日前', 79067), ('起', 79002), ('一种', 78923), ('电话', 78827), ('今天', 78734), ('提出', 78697), ('水平', 78277), ('副', 78207), ('预期', 78190), ('知道', 78089), ('当时', 78039), ('加强', 77920), ('采用', 77826), ('第一', 77746), ('英国', 77603), ('负责人', 77520), ('成功', 77303), ('期间', 77074), ('那', 76900), ('提升', 76636), ('客户', 76587), ('稳定', 76241), ('如', 75598), ('专家', 75586), ('下午', 75577), ('万股', 75430), ('指数', 75414), ('之前', 74774), ('发行', 74771), ('车身', 74645), ('准备', 74500), ('具有', 74480), ('参与', 74420), ('不仅', 74223), ('重点', 74130), ('连续', 73972), ('未', 73960), ('历史', 73568), ('必须', 73560), ('动力', 73458), ('整体', 73436), ('类', 73223), ('新闻', 73223), ('修改', 73192), ('人民币', 72793), ...]
```

- 没有停用词与筛选。

### 11.10 简化新闻的时间折线图

- 由于完整新闻运行的时间过长，此处简化新闻数据，即建立100个txt文件，每个文件中仅保存100条新闻，观察Map进程数量从1至50的运行时间变化情况：

<img src="https://s2.loli.net/2022/01/29/9zlpeqAZ7FboJj3.png" alt="Time" style="zoom:15%;" />

- 当Map进程数接近`os.cpu_count`时，运行速度最快，而进程数比cpu数量越小越大，则运行时间均增加；
- 当Map进程数小于cpu数量，时间——进程数大致服从$y=1/x$；
- 当Map进程数大于cpu数量，时间——进程数大致服从线性关系。
