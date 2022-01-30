## 第十二次作业 网易云歌单爬虫——多线程

### 12.1 大致框架——生产者-消费者模型

```python
pic_num = 1

class Producer(Thread):
    '''
    获取一个分类下的所有歌单的id，
    作为生产者-消费者模型的生产者。
    '''
    def __init__(self, name, cat, pq: Queue, urlq: Queue):
        super().__init__()

    @property
    def name(self):
        pass

    def get_page(self):
        pass

    def crawl_url(self, page):
        pass

    def run(self):
        pass

class Consumer(Thread):
    '''
    对每个id，获取歌单的详细信息，
    至少包括：歌单的封面图片（需把图片保存到本地）、歌单标题、创建者id、
             创建者昵称、介绍、歌曲数量、播放量、添加到播放列表次数、
             分享次数、评论数。
    作为生产者-消费者模型的生产者。
    '''
    def __init__(self, name, urlq: Queue, res_csv, csv_lock: Lock):
        super().__init__()

    @property
    def name(self):
        return self._name

    def download_cover(self, url):
        global pic_num
        pass

    def crawl_features(self, url):
        pass

    def get_time(self, time):
        pass

    def get_id(self, id):
        pass

    def write_csv(self, dic):
        pass

    def run(self):
        pass

def main():
    pass

if __name__ == "__main__":
    main()
```

- Producer作为模型的生产者，其功能在于获取一个分类下的所有歌单的id；
- Consumer作为模型的消费者，其功能在于对每个id，获取歌单的详细信息；
- 建立两个队列：`page_queue, url_queue`，分别用于页码的传输与每页对应url的传输。

### 12.2 Producer类

```python
class Producer(Thread):
    '''
    获取一个分类下的所有歌单的id，
    作为生产者-消费者模型的生产者。
    '''
    def __init__(self, name, cat, pq: Queue, urlq: Queue):
        super().__init__()
        self._name = "P-{0:>2d}".format(name)
        self.pq = pq
        self.urlq = urlq
        self.cat = cat
        self.cat_url = "https://music.163.com/discover/playlist/?cat=" \
                        + self.cat + "&limit=35&"
        self.base_url = "https://music.163.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
            "Referer": "https://music.163.com/",
            "Upgrade-Insecure-Requests": '1'
        }

    @property
    def name(self):
        return self._name

    def get_page(self):
        page = self.pq.get()
        if page is None:
            return
        else:
            return page

    def crawl_url(self, page):
        offset = 35*page
        url = self.cat_url + f"offset={offset}"
        html = requests.get(url, headers=self.headers).text
        html_elem = etree.HTML(html)
        hrefs = html_elem.xpath('//*[@id="m-pl-container"]/li/div/a/@href')
        while len(hrefs) == 0:
            html = requests.get(url, headers=self.headers).text
            html_elem = etree.HTML(html)
            hrefs = html_elem.xpath('//*[@id="m-pl-container"]/li/div/a/@href')
        for href in hrefs:
            playlist_url = self.base_url + href
            self.urlq.put(playlist_url)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
                  f"  {self.name} put {playlist_url} into url queue.")

    def run(self):
        while True:
            page = self.get_page()
            if page is None:
                self.urlq.put(None)
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
                      f"  {self.name} has done its work and put None into url queue.")
                break
            else:
                self.crawl_url(page)
```

#### 12.2.1 \__init__

- 初始化`page_queue`, `url_queue`，以及需要爬取的`url`和`headers`；

#### 12.2.2 get_page

- page从`page_url`中获取；

#### 12.2.3 crawl_url

- 获取每页中全部歌单的url，并传入`url_queue`；

#### 12.2.4 run

- 持续循环执行`get_page`方法，若返回`None`则此Producer停止；

- 具体功能交给`get_page`和`crawl_url`处理。

### 12.3 Consumer类

```python
class Consumer(Thread):
    '''
    对每个id，获取歌单的详细信息，
    至少包括：歌单的封面图片（需把图片保存到本地）、歌单标题、创建者id、
             创建者昵称、介绍、歌曲数量、播放量、添加到播放列表次数、
             分享次数、评论数。
    作为生产者-消费者模型的生产者。
    '''
    def __init__(self, name, urlq: Queue, res_csv, pic_lock: Lock):
        super().__init__()
        self._name = "C-{0:>2d}".format(name)
        self.urlq = urlq
        self.res_csv = res_csv
        self.pic_lock = pic_lock
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
            "Referer": "https://music.163.com/",
            "Upgrade-Insecure-Requests": '1'
        }

    @property
    def name(self):
        return self._name

    def download_cover(self, url):
        with self.pic_lock:
            global pic_num
            img = requests.get(url=url, headers=self.headers).content
            with open(f"./covers/{pic_num}.png", "wb") as f:
                f.write(img)
                pic_num += 1

    def crawl_features(self, url):
        html = requests.get(url, headers=self.headers).text
        html_elem = etree.HTML(html)
        
        try:
            title = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[1]/div/h2/text()')[0]
            author_name = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[2]/span[1]/a/text()')[0]
            author_id = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[2]/span[1]/a/@href')[0]
            author_id = self.get_id(author_id)
            cover_URL = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/img/@data-src')[0]

            self.download_cover(cover_URL)

            created_time = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[2]/span[2]/text()')[0]
            created_time = self.get_time(created_time)
            intro = html_elem.xpath('/html/head/meta[18]/@content')[0]

            favored_num = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[3]/a[3]/i/text()')[0]
            if favored_num == "收藏":
                favored_num = 0
            else:
                favored_num = favored_num[1:-1]

            forward_num = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[3]/a[4]/i/text()')[0]
            if forward_num == "分享":
                forward_num = 0
            else:
                forward_num = forward_num[1:-1]

            comments_num = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[3]/a[6]/i/span/text()')[0]
            if comments_num == "评论":
                comments_num = 0

            tags = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[4]/a/i/text()')
            songs_num = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[1]/span/span/text()')[0]
            play_num = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[1]/div[1]/strong/text()')[0]
        except:
            print("error url:", url)

        return {
            "title": title, 
            "created_time": created_time, 
            "author_ID": author_id, 
            "author_name": author_name, 
            "intro": intro, 
            "tags": tags, 
            "songs_num": songs_num, 
            "play_num": play_num, 
            "favored_num": favored_num, 
            "forward_num": forward_num, 
            "comments_num": comments_num, 
            "cover_URL": cover_URL
            }

    def get_time(self, time):
        return time[:10]

    def get_id(self, id):
        author_id = ""
        for c in reversed(id):
            if c == "=":
                break
            author_id = c + author_id
        return author_id

    def write_csv(self, dic):
        headers = ["title", "created_time", "author_ID", "author_name", "intro", "tags", 
                   "songs_num", "play_num", "favored_num", "forward_num", "comments_num", "cover_URL"]
        rows = [dic[ele] for ele in headers]
        with self.csv_lock:
            self.res_csv.writerow(rows)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
              f"  {self.name} has written a result into csvfile.")

    def run(self):
        while True:
            url = self.urlq.get()
            if url is None:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
                      f"  {self.name} has done its work.")
                break
            else:
                feat_dic = self.crawl_features(url)
                self.write_csv(feat_dic)
```

#### 12.3.1 \__init__

- 初始化`url_queue`, `res_csv`, `pic_lock`, `headers`，对应于url队列、csv文件、保存图片的锁与爬虫头部；

#### 12.3.2 crawl_features

- 从url中爬取对应歌单的信息，并通过`download_cover`、`get_id`、`get_time`和`write_csv`来下载歌单封面、获取id、获取发布时间以及csv文件的写入；

#### 12.3.3 run

- 持续循环执`self.urlq.get()`，若返回`None`则此Consumer停止；
- 利用方法`self.crawl_features`和`self.write_csv`方法。

### 12.4 main函数

```python
def main():
    producer_num = 30
    consumer_num = 30
    cat = "古典"
    page_queue = Queue()
    url_queue = Queue()
    pic_lock = Lock()
    for i in range(38):
        page_queue.put(i)
    for i in range(producer_num):
        page_queue.put(None)

    producers = []
    for i in range(producer_num):
        p = Producer(i, cat, page_queue, url_queue)
        producers.append(p)
    for p in producers:
        p.start()

    res = open("Classic.csv", mode="w", newline="", encoding="GB18030")
    res_csv = csv.writer(res)
    headers = ["title", "created_time", "author_ID", "author_name", "intro", "tags", 
               "songs_num", "play_num", "favored_num", "forward_num", "comments_num", "cover_URL"]
    res_csv.writerow(headers)

    consumers = []
    for i in range(consumer_num):
        c = Consumer(i, url_queue, res_csv, pic_lock)
        consumers.append(c)
    for c in consumers:
        c.start()

    for c in consumers:
        c.join()
    for p in producers:
        p.join()

    res.close()
```

- 将0-37插入`page_url`中，选取古典作为`cat`，实例化Producer和Consumer，并且`start`和`join`；
- 打开`Classic.csv`，传入Consumer中。

### 12.5 包管理

```python
import csv
import time
import requests
from lxml import etree
from queue import Queue
from threading import Thread, Lock
```

### 12.6 结果展示

#### 12.6.1 csv文件

![](https://s2.loli.net/2022/01/29/IGHnfLUmBAkpZxD.png)

<center>......</center>

![](https://s2.loli.net/2022/01/29/WMR6xlOUmZi9YtE.png)

- 共$35\times37+15=1310$行数据，即1310个歌单；

#### 12.6.2 图片

![](https://s2.loli.net/2022/01/29/BMdtCj5FRfbr4s1.png)

<img src="https://s2.loli.net/2022/01/29/aDuYIewThMgSsmO.png" style="zoom:80%;" />

