## 第九次作业 生成器与迭代器

### 9.1 生成随机游走的迭代器函数

#### 9.1.1 random_walk生成器

```python
import random

def random_walk(mu, X0, sigma2, N):
    n = 0
    while (n < N):
        wt = random.normalvariate(0, (sigma2)**0.5)
        X1 = mu + X0 + wt
        yield X0
        X0 = X1
        n += 1
    return "done"

if __name__ == "__main__":
    rw = random_walk(0.1, 3, 4, 10)
    while True:
        try:
            print(next(rw))
        except StopIteration as si:
            print(si.value)
            break
```

- 以$\mu=0.5,\ X_0=3,\ \sigma^2=4,\ N=10$为例，结果如下：

  ```python
  6.149369802670318
  5.430295009516424
  7.096326569627065
  7.759744845193579
  9.638937660305135
  9.723530483384263
  11.310995271835267
  11.311351108947735
  9.363471191069976
  10.069195551081572
  done
  ```

- 以$\mu=0.1,\ X_0=3,\ \sigma^2=4,\ N=100$为例作图，有：

<img src="https://s2.loli.net/2022/01/29/YlKSUE2kFmvRWjy.png" alt="one-dim" style="zoom: 10%;" />

#### 9.1.2 拼合多个random_walk的生成器

- 定义函数`zip_random_walk`，其中假如参数`M`，代表生成M维时间上对齐的多维随机游走序列：

```python
def zip_random_walk(mu, X0, sigma2, N, M):
    # M维时间上对齐的多维随机游走序列
    gen_list = []
    for i in range(M):
        gen_list.append(random_walk(mu, X0, sigma2, N))
    z = zip(*gen_list)
    return z

if __name__ == "__main__":
    z = zip_random_walk(0.1, 3, 4, 5, 3)
    while True:
        try:
            print(next(z))
        except StopIteration as si:
            print("Done")
            break
```

- 以$\mu=0.1,\ X_0=3,\ \sigma^2=4,\ N=5,\ M=3$为例，结果如下：

  ```python
  (4.501558632480093, 2.95147448377889, 5.739108335728112)
  (3.957136288078387, 5.600078573109096, 5.649541533668884)
  (6.881690196463257, 8.44538032576697, 3.73131585442084)
  (8.915927477368262, 6.615206814976662, 3.554332169292542)
  (10.08962589567992, 7.496200746099414, 4.603644638335721)
  Done
  ```

- 以$\mu=1,\ X_0=1,\ \sigma^2=200,\ N=100,\ M=6$为例作图，有：

<img src="https://s2.loli.net/2022/01/29/UcWYBhdu5tIMmws.png" alt="high-dim" style="zoom:10%;" />

### 9.2 FaceDataset类

```python
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
        if self._i <= self._n:
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
```

- 其中定义了两个内部方法`__get_path`和`__converter`，分别获取所有图片的路径组成的列表与图片对应`ndarray`：
  - `__get_path`中利用`os.walk`通过在目录树中游走获取文件名，再通过`os.path.join`拼接为绝对路径，为`Image.open`做准备；
  - `__converter`中利用`Image.open`与`np.array`函数返回图片对应矩阵；
- `__next__`与`__iter__`实现了迭代器。

```python
全部路径获取成功！
 29%|████████████████████████                                                           | 8183/28204 [00:28<03:15, 102.25it/s]
```

- 返回的`ndarray`如下所示：

```
[[ 23  30  23]
  [ 23  30  23]
  [ 23  30  23]
  ...
  [ 70  78  57]
  [ 71  78  60]
  [ 73  80  62]]

 [[ 23  30  23]
  [ 23  30  23]
  [ 23  30  23]
  ...
  [ 68  76  55]
  [ 69  76  58]
  [ 70  77  59]]

 [[ 23  30  23]
  [ 23  30  23]
  [ 23  30  23]
  ...
  [ 65  73  52]
  [ 66  73  55]
  [ 68  75  57]]

 ...

 [[126 142  71]
  [126 142  71]
  [126 142  71]
  ...
  [110 125  58]
  [110 125  58]
  [110 125  58]]

 [[128 139  70]
  [129 140  71]
  [130 141  72]
  ...
  [117 132  63]
  [117 132  63]
  [117 133  62]]

 [[128 139  70]
  [129 140  71]
  [130 141  72]
  ...
  [117 132  63]
  [117 132  63]
  [117 133  62]]]
```

