## 第十五次作业 Bilibili热榜——非关系数据库编程

### 15.1 大致框架

- 引用Hobee学长关于协程爬取Bilibili热榜、邮件发送功能的代码；
- 将Hobee学长写入csv的代码修改为存入MongoDB；
- 完成从数据库中取出数据的操作；
- 完成新数据与取出数据对比并更新数据库的操作。

### 15.2 代码实现

#### 15.2.1 分区选取

- 选取运动区中的篮球·足球

| 分区名  | 篮球·足球                                                    |
| ------- | ------------------------------------------------------------ |
| 代号    | basketballfootball                                           |
| tid     | 235                                                          |
| 简介    | 与篮球、足球相关的视频，包括但不限于篮足球赛事、教学、评述、剪辑、剧情等相关内容 |
| url路由 | /v/sports/                                                   |

#### 15.2.2 类BiliHotCrawler

```python
class BiliHotCrawler():
    def __init__(self,cate,collection,limit=10000):
        self.cate_id = cate
        self.limit = limit
        self.page = 1
        self.pagesize = 100
        self.bulid_param()
        self.url = BASE_URL
        self.collection = collection
        
    def bulid_param(self):
        self.params = {
            'main_ver':'v3',
            'search_type':'video',
            'view_type':'hot_rank',
            'order':'click',
            'cate_id':self.cate_id,
            'page':self.page,
            'pagesize':self.pagesize,
            'time_from':20211220,
            'time_to':20211227, 
        }

    async def get_resp(self):
        time.sleep(random.choice(sleep_choice))
        self.bulid_param()
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.url,params=self.params) as response:
                self.resp = await response.read()
        self.page += 1

    def save_resp_to_db(self):
        self.resp = eval(
            self.resp.decode(ENCODING)
            .replace('null','None')
            .replace('false',"False")
            .replace("true","True")
            .replace("\n"," ")
        )
        temp = []
        for item in self.resp["result"]:
            dic = {
                "rank_offset": 0, 
                "bvid": 0, 
                "duration": 0, 
                "play": 0, 
                "video_review": 0, 
                "title": 0, 
                "pic": 0, 
                "review": 0, 
                "favorites": 0, 
                "description": 0, 
                "arcurl": 0, 
                "create_time": 0, 
            }
            for i in dic:
                if i == "title" or i == "description":
                    dic[i] = item[i].replace("\n"," ").encode(ENCODING, 'replace').decode(ENCODING)
                    continue
                if i == "create_time":
                    dic[i] = self.params["time_to"]
                    continue
                dic[i] = item[i]
            temp.append(dic)
        temp = sorted(temp, key=lambda x:x["rank_offset"])
        self.collection.insert_many(temp)

    def take_out(self):
        self.old_gen = self.collection.find()
        self.old_bvid = []
        while True:
            try:
                self.old_bvid.append(next(self.old_gen)["bvid"])
            except StopIteration as SI:
                break
        self.collection.delete_many({})

    def update(self):
        self.resp = eval(
            self.resp.decode(ENCODING)
            .replace('null','None')
            .replace('false',"False")
            .replace("true","True")
            .replace("\n"," ")
        )
        temp = []
        for item in self.resp["result"]:
            bvid = item["bvid"]
            if bvid in self.old_bvid:
                flag = 1
            else:
                flag = 0

            dic = {
                "rank_offset": 0, 
                "bvid": 0, 
                "duration": 0, 
                "play": 0, 
                "video_review": 0, 
                "title": 0, 
                "pic": 0, 
                "review": 0, 
                "favorites": 0, 
                "description": 0, 
                "arcurl": 0, 
                "create_time": 0, 
                "update_time": 0, 
            }
            for i in dic:
                if i == "title" or i == "description":
                    dic[i] = item[i].replace("\n"," ").encode(ENCODING, 'replace').decode(ENCODING)
                    continue
                if i == "create_time":
                    if flag == 0:
                        dic[i] = self.params["time_to"]
                    else:
                        dic[i] = 20211220
                    continue
                if i == "update_time":
                    if flag == 0:
                        continue
                    else:
                        dic[i] = self.params["time_to"]
                        continue
                dic[i] = item[i]
            temp.append(dic)
        temp = sorted(temp, key=lambda x:x["rank_offset"])
        self.collection.insert_many(temp)

    def log(self,isend=False):
        print(f"\rCrawlering {self.cate_id} {(self.page - 1)*self.pagesize}/{self.limit}", end="")
        if isend:
            print()

    async def start(self):
        self.take_out()
        while self.pagesize * self.page <= self.limit:
            self.log()
            await self.get_resp()
            #self.save_resp()
            #self.save_resp_to_db()
            self.update()
        self.log(isend=True)
```

- `save_resp_to_db`方法将爬取的10000条信息经过格式转化以集合形式存入数据库中；
- `take_out`方法将数据库中全部信息取出并存入内存中；
- `update`方法将新爬取的数据与内存中数据对比，并更新数据库。

#### 15.2.3 类BHCFactory (Copyright Hobee)

```python
class BHCFactory():
    def __init__(self,cate_list,collection):
        self.cate_list = cate_list
        self.collection = collection

    def produce(self): # 相当于开了多个协程去分别爬取每个板块的热榜
        loop = asyncio.get_event_loop()
        tasks = [BiliHotCrawler(i, self.collection).start() for i in self.cate_list]
        loop.run_until_complete(asyncio.wait(tasks))
```

- `BiliHotCrawler`的工厂模式类，开多个协程去分别爬取每个板块的热榜。

#### 15.2.4 类BiliNoticeMail (Copyright Hobee)

```python
class BiliNoticeMail:
    def __new__(cls, *args, **kwargs):
        if not hasattr(BiliNoticeMail, '_instance'):
            BiliNoticeMail._instance = object.__new__(cls, *args, **kwargs)
        return BiliNoticeMail._instance

    def __init__(self):
        self.server = SMTP_SSL(SMTP_SERVER, PORT)
        self.message = None
        pass

    def build_ready_message(self):
        self.message = MIMEText('下载完成', 'plain', ENCODING)
        self.message['From'] = Header(FROM_ADDR, ENCODING)
        self.message['To'] = Header(TO_ADDR, ENCODING)
        self.message['Subject'] = Header('BiliReminder:Ready', ENCODING)

    def notice(self):
        if self.message is None:
            raise ValueError('Message is none!')
        self.server.login(FROM_ADDR, PASSWD)
        self.server.sendmail(FROM_ADDR, [TO_ADDR], self.message.as_string())
        self.message = None
        self.server.quit()

    @classmethod
    def send_ready_mail(cls):
        noticer = cls()
        noticer.build_ready_message()
        noticer.notice()
        print("发信成功，请查收。")
        return noticer
```

- 若运行结束则发送“发信成功，请查收。”至邮箱。

#### 15.2.5 全局变量

```python
BASE_URL = 'https://s.search.bilibili.com/cate/search'
CATE_LIST = [235]
sleep_choice = [1, 2, 3, 4, 5]
ENCODING = "GB2312"

# Email Configer
SMTP_SERVER = 'smtp.163.com'
PORT = 465
FROM_ADDR = 'kaixin2001_2012@163.com'
PASSWD = '********'
TO_ADDR = 'kaixin2001_2012@163.com'
```

#### 15.2.6 main()与包管理

```python
import os
import time
import requests as rs
import asyncio
import aiohttp
import random
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from pymongo import MongoClient

def main():
    client = MongoClient('localhost', 27017)
    db = client.bilibili
    collection = db.hot
    BHCFactory(CATE_LIST, collection).produce()
    BiliNoticeMail.send_ready_mail()

if __name__ == '__main__':
    main()
```

- 建立数据库`bilibili`和集合`hot`，启动`BHC`工厂并开启协程爬虫，最终发送邮件。

### 15.3 结果展示

- 2021年12月13日至2021年12月20日篮球·足球分区的热榜前10000信息

![image-20220102154429658](https://s2.loli.net/2022/01/29/1mFyCjI8qDvaxSe.png)

![image-20220102154518324](https://s2.loli.net/2022/01/29/HfQNtcRgyeIBKM3.png)

- 数据库状态与运行结果

![image-20220102150445948](https://s2.loli.net/2022/01/29/qclh2MLnD3RUGSv.png)

![image-20220102150547170](https://s2.loli.net/2022/01/29/YXtmqdUh4zlgfZa.png)

- 邮件

![image-20220102150626281](https://s2.loli.net/2022/01/29/mzZ61pdMfV5Ayxe.png)

- 2021年12月20日至2021年12月27日篮球·足球分区的热榜前10000信息，更新数据库

![image-20220102163447291](https://s2.loli.net/2022/01/29/m98HFnjkqiWxRw7.png)

![image-20220102163504211](https://s2.loli.net/2022/01/29/IbzkhdPR148erAV.png)

