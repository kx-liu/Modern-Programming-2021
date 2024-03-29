import csv
import time
import requests
from lxml import etree
from queue import Queue
from threading import Thread, Lock

pic_num = 1

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

if __name__ == "__main__":
    main()