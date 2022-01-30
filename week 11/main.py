import os
import sys
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

def count_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        fun_res = func(*args, **kwargs)
        end = time.time()
        print(f"func {func.__name__} running time: {end-start} sec.")
        return fun_res
    return wrapper

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

if __name__ == "__main__":
    main()