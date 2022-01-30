import os
from PIL import Image
import numpy as np
from tqdm import tqdm

class FaceDataset:
    '''
    采用批量加载数据的方法实现图片数据的加载
    '''
    def __init__(self, path):
        self.path = path
        self._path_list = self.__get_path()
        self._i = 0
        self._n = len(self._path_list)

    def __iter__(self):
        return self

    def __next__(self):
        if self._i < self._n:
            ndarray = self.__converter(self._path_list[self._i])
            self._i += 1
            return ndarray
        else:
            raise StopIteration(f"迭代完毕，共{self._n}次")

    def __get_path(self):
        '''
        接收图片路径列表
        '''
        iter = os.walk(self.path)
        path_list = []
        while True:
            try:
                ls = next(iter)
                if len(ls[1]) != 0:
                    continue
                for p in ls[2]:
                    abs_path = os.path.join(ls[0], p)
                    path_list.append(abs_path)
            except StopIteration:
                print("全部路径获取成功！")
                break
        return path_list

    def __converter(self, image):
        '''
        将一张图片数据以ndarray的形式返回
        '''
        im = Image.open(image)
        return np.array(im)

if __name__ == "__main__":
    fd = FaceDataset("D:\\vscode py\\现代程设\\week 9\\originalPics")
    with tqdm(total=fd._n) as bar:
        for x in fd:
            bar.update(1)
            print(x)
            break
