import random
import pickle
# from line_profiler import LineProfiler
from memory_profiler import profile
from tqdm import tqdm
import time
from functools import wraps
import os
from playsound import playsound

class PathChecker:
    '''
    接收函数的路径参数，检查路径对应文件夹是否存在，
    若不存在，则给出提示，并在提示后由系统自动创建对应的文件夹。
    '''
    def __init__(self):
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            path = args[2]
            if not os.path.exists(path):
                print("path do not exist, automatically create it for you")
                os.mkdir(path)
                print("created successfully")
            return func(*args, **kwargs)
        return wrapper

class PlaySound:
    '''
    在被装饰的函数执行结束后，主动播放声音。
    '''
    def __init__(self):
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            f = func(*args, **kwargs)
            playsound("champion.mp3")
            return f
        return wrapper

class Disaster:
    '''
    提供一些方法模拟耗时耗内存的一些操作，以测试如下装饰器
    '''
    def __init__(self):
        pass

    @PlaySound()
    def data_structure_generator(self, m, n):
        '''
        生成大型数据结构
        '''
        ds = [[random.randint(0,100) for i in range(m)] for j in tqdm(range(n))]
        return ds

    def traverse(self, ds):
        '''
        遍历大型数据结构
        '''
        m = len(ds)
        n = len(ds[0])
        with tqdm(total=m*n) as bar:
            for i in range(m):
                for j in range(n):
                    bar.update(1)

    @PathChecker()
    def serilizer(self, ds, path):
        '''
        序列化大型数据结构
        '''
        with open(path+"ds.txt", "wb") as f:
            pickle.dump(ds, f)

if __name__ == "__main__":
    d = Disaster()
    ds = d.data_structure_generator(10, 10)
    d.traverse(ds)
    d.serilizer(ds, "D:\\vscode py\\现代程设\\week 8\\fake path\\")