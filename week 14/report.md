## 第十四次作业 网易云爬虫——协程

### 14.1 大致框架

- 分为两个`.py`文件；
- 文件一：`netease_get_playlist.py`，其功能为第十二次作业的功能，并将其以协程的形式重新实现；
- 文件二：`netease_get_hot.py`，其功能为读取文件一生成的csv文件，设立评价为热门歌单的阈值并获取之，得到其前十歌曲的特征；

### 14.2 netease_get_playlist.py

```python
import csv
import asyncio
import aiohttp
import aiofiles
from lxml import etree
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

pic_num = 0
url_list = []
play_list = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Referer": "https://music.163.com/",
    "Upgrade-Insecure-Requests": '1'
}

async def crawl_url(url):
    global url_list
    conn=aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()
            html_elem = etree.HTML(html)
            hrefs = html_elem.xpath('//*[@id="m-pl-container"]/li/div/a/@href')
            if len(hrefs) == 0:
                pass
            else:
                for href in hrefs:
                    url_list.append("https://music.163.com"+href)

async def crawl_features(url):
    global play_list
    conn=aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()
            html_elem = etree.HTML(html)
            try:
                title = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[1]/div/h2/text()')[0]
                author_name = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[2]/span[1]/a/text()')[0]
                author_id = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[2]/span[1]/a/@href')[0]
                author_id = get_id(author_id)
                cover_URL = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/img/@data-src')[0]

                await download_cover(cover_URL)

                created_time = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[2]/div/div[2]/span[2]/text()')[0]
                created_time = get_time(created_time)
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

                features =  {
                    "URL": url, 
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
                play_list.append(features)

            except:
                print("error url:", url)

async def download_cover(url):
    global pic_num
    conn=aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
        async with session.get(url) as response:
            img = await response.read()
            async with aiofiles.open(f"D:/vscode py/现代程设/week 14/covers/{pic_num}.jpg", mode='wb') as f:
                await f.write(img)
                pic_num += 1

def get_time(time):
    return time[:10]

def get_id(id):
    author_id = ""
    for c in reversed(id):
        if c == "=":
            break
        author_id = c + author_id
    return author_id

def write_csv():
    headers = ["URL", "title", "created_time", "author_ID", "author_name", "intro", "tags", 
               "songs_num", "play_num", "favored_num", "forward_num", "comments_num", "cover_URL"]
    res = open("D:/vscode py/现代程设/week 14/Classic.csv", mode="w", newline="", encoding="GB18030")
    res_csv = csv.writer(res)
    res_csv.writerow(headers)
    for feat in play_list:
        rows = [feat[ele] for ele in headers]
        res_csv.writerow(rows)
    res.close()

def main():
    loop = asyncio.get_event_loop()
    cat_url = "https://music.163.com/discover/playlist/?cat="\
              + "古典" + "&limit=35&"
    urls = [cat_url + f"offset={i*35}" for i in range(37)]
    tasks = [loop.create_task(crawl_url(url)) for url in urls]
    loop.run_until_complete(asyncio.wait(tasks))

    loop2 = asyncio.get_event_loop()
    tasks2 = [loop.create_task(crawl_features(url)) for url in url_list]
    loop2.run_until_complete(asyncio.wait(tasks2))

    write_csv()

if __name__ == "__main__":
    main()
```

- 结果展示：

![image-20220101205313263](https://s2.loli.net/2022/01/29/bR2pwWAxkoTiSL5.png)

![image-20220101205346320](https://s2.loli.net/2022/01/29/7M3GjerhIcYXltQ.png)

### 14.3 netease_get_hot.py

```python
import csv
import asyncio
import aiohttp
from lxml import etree
from bs4 import BeautifulSoup
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Referer": "https://music.163.com/",
    "Upgrade-Insecure-Requests": '1'
}

url_list = []
song_list = []

def read_csv():
    with open("D:/vscode py/现代程设/week 14/Classic.csv", encoding="GB18030") as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            analyze_csv(row)

def analyze_csv(row):
    global url_list
    try:
        play_num = int(row[8])
        if play_num >= 1000000:
            url_list.append(row[0])
    except ValueError:
        print(row[7], "\tValueError")

async def crawl_url(url):
    global song_list
    conn=aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()
            s = BeautifulSoup(html, "lxml")
            try:
                main = s.find("ul", {'class': 'f-hide'})
                for music in main.find_all('a'):
                    song_url = music['href'].split("\n")
                    for url in song_url:
                        url = "https://music.163.com"+url
                        dic = await crawl_song(url)
                        song_list.append(dic)
            except:
                print(url, "\tError!")

async def crawl_song(url):
    conn=aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()
            html_elem = etree.HTML(html)
            try:
                title = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/div[1]/div/em/text()')[0]
                author = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/p[1]/span/a/text()')[0]
                album = html_elem.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/p[2]/a/text()')[0]
                feature = {
                    "URL": url, 
                    "title": title, 
                    "author": author, 
                    "album": album, 
                }
                return feature
            except:
                print(url, "\tError!")

def write_csv():
    headers = ["URL", "title", "author", "album"]
    res = open("D:/vscode py/现代程设/week 14/Classic_hot.csv", mode="w", newline="", encoding="GB18030")
    res_csv = csv.writer(res)
    res_csv.writerow(headers)
    for song in song_list:
        try:
            rows = [song[ele] for ele in headers]
            res_csv.writerow(rows)
        except:
            print("ERROR!!")
            continue
    res.close()

def main():
    read_csv()

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(crawl_url(url)) for url in url_list]
    loop.run_until_complete(asyncio.wait(tasks))

    write_csv()

if __name__ == "__main__":
    main()
```

- 结果展示

![image-20220101205709573](https://s2.loli.net/2022/01/29/3tN1ALD4QO9drKs.png)
