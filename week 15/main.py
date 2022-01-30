"""
名称  代号  tid 简介  url路由
运动(主分区)	sports	234		/v/sports
篮球·足球	basketballfootball	235	与篮球、足球相关的视频，包括但不限于篮足球赛事、教学、评述、剪辑、剧情等相关内容	/v/sports/basketballfootball
健身	aerobics	164	与健身相关的视频，包括但不限于瑜伽、CrossFit、健美、力量举、普拉提、街健等相关内容	/v/sports/aerobics
竞技体育	athletic	236	与竞技体育相关的视频，包括但不限于乒乓、羽毛球、排球、赛车等竞技项目的赛事、评述、剪辑、剧情等相关内容	/v/sports/culture
运动文化	culture	237	与运动文化相关的视频，包络但不限于球鞋、球衣、球星卡等运动衍生品的分享、解读，体育产业的分析、科普等相关内容	/v/sports/culture
运动综合	comprehensive	238	与运动综合相关的视频，包括但不限于钓鱼、骑行、滑板等日常运动分享、教学、Vlog等相关内容	/v/sports/comprehensive
"""

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

SAVE_PATH = 'D:/vscode py/现代程设/week 15/data_csv/'
BASE_URL = 'https://s.search.bilibili.com/cate/search'
CATE_LIST = [235]
sleep_choice = [1, 2, 3, 4, 5]
ENCODING = "GB2312"

# Email Configer
SMTP_SERVER = 'smtp.163.com'
PORT = 465
FROM_ADDR = 'kaixin2001_2012@163.com'
PASSWD = '**'
TO_ADDR = 'kaixin2001_2012@163.com'

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

    def save_resp(self):
        path = f"{SAVE_PATH}/{self.cate_id}.csv"
        with open(path,"a",errors='ignore') as f:
            self.resp = eval(
                self.resp.decode(ENCODING)
                .replace('null','None')
                .replace('false',"False")
                .replace("true","True")
                .replace("\n"," ")
            )
            replr = "\r"
            for item in self.resp["result"]:
                # 分类 排名 bv号 时长 播放量 弹幕 标题 封面 评论 收藏 描述 直链
                f.write(
                    f'{self.cate_id},\
                      {item["rank_offset"]},\
                      {item["bvid"]},\
                      {item["duration"]},\
                      {item["play"]},\
                      {item["video_review"]},\
                      {item["title"]},\
                      {item["pic"]},\
                      {item["review"]},\
                      {item["favorites"]},\
                      {item["description"]},\
                      {item["arcurl"]}'
                      .replace("\n"," ").encode(ENCODING, 'replace').decode(ENCODING))
                f.write("\n")

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


class BHCFactory():
    def __init__(self,cate_list,collection):
        self.cate_list = cate_list
        self.collection = collection

    def produce(self): # 相当于开了多个协程去分别爬取每个板块的热榜
        loop = asyncio.get_event_loop()
        tasks = [BiliHotCrawler(i, self.collection).start() for i in self.cate_list]
        loop.run_until_complete(asyncio.wait(tasks))


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

def main():
    client = MongoClient('localhost', 27017)
    db = client.bilibili
    collection = db.hot
    BHCFactory(CATE_LIST, collection).produce()
    BiliNoticeMail.send_ready_mail()

if __name__ == '__main__':
    main()
