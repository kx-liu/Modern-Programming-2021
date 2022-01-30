## 第八次作业 装饰器

### 8.1 模拟耗时耗内存的类

```python
class Disaster:
    '''
    提供一些方法模拟耗时耗内存的一些操作，以测试如下装饰器
    '''
    def __init__(self):
        pass

    def data_structure_generator(self, m, n):
        '''
        生成大型数据结构
        '''
        ds = [[random.randint(0,100) for i in range(m)] for j in range(n)]
        return ds

    def traverse(self, ds):
        '''
        遍历大型数据结构
        '''
        m = len(ds)
        n = len(ds[0])
        for i in range(m):
            for j in range(n):
                pass

    def serilizer(self, ds):
        '''
        序列化大型数据结构
        '''
        with open("ds.txt", "wb") as f:
            pickle.dump(ds, f)
```

### 8.2 line_profiler

- 利用`line_profiler`库，通过装饰器`@profile`来实现，同时通过命令行语句`kernprof –lv ld.py`

```python
Wrote profile results to decorate.py.lprof
Timer unit: 1e-06 s

Total time: 0.0352583 s
File: decorate.py
Function: data_structure_generator at line 16

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    16                                               @profile # memory_profiler
    17                                               def data_structure_generator(self, m, n):
    18                                                   '''
    19                                                   生成大型数据结构
    20                                                   '''
    21         1      35256.9  35256.9    100.0          ds = [[random.randint(0,100) for i in range(m)] for j in range(n)]    
    22         1          1.4      1.4      0.0          return ds

Total time: 0.005987 s
File: decorate.py
Function: traverse at line 24

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    24                                               @profile
    25                                               def traverse(self, ds):
    26                                                   '''
    27                                                   遍历大型数据结构
    28                                                   '''
    29         1          1.0      1.0      0.0          m = len(ds)
    30         1          0.7      0.7      0.0          n = len(ds[0])
    31       101         29.5      0.3      0.5          for i in range(m):
    32     10100       3050.7      0.3     51.0              for j in range(n):
    33     10000       2905.1      0.3     48.5                  pass

Total time: 0.0078679 s
File: decorate.py
Function: serilizer at line 35

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    35                                               @profile
    36                                               def serilizer(self, ds):
    37                                                   '''
    38                                                   序列化大型数据结构
    39                                                   '''
    40         1        289.8    289.8      3.7          with open("ds.txt", "wb") as f:
    41         1       7578.1   7578.1     96.3              pickle.dump(ds, f)
```

### 8.3 memory_profiler

- 利用`memory_profiler`库，通过装饰器`@profile`来实现。

```python
Filename: d:/vscode py/现代程设/week 8/decorate.py

Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    16     41.4 MiB     41.4 MiB           1       @profile # memory_profiler
    17                                             def data_structure_generator(self, m, n):
    18                                                 '''
    19                                                 生成大型数据结构
    20                                                 '''
    21     41.4 MiB      0.0 MiB       10303           ds = [[random.randint(0,100) for i in range(m)] for j in range(n)]      
    22     41.4 MiB      0.0 MiB           1           return ds


Filename: d:/vscode py/现代程设/week 8/decorate.py

Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    24     41.4 MiB     41.4 MiB           1       @profile
    25                                             def traverse(self, ds):
    26                                                 '''
    27                                                 遍历大型数据结构
    28                                                 '''
    29     41.4 MiB      0.0 MiB           1           m = len(ds)
    30     41.4 MiB      0.0 MiB           1           n = len(ds[0])
    31     41.4 MiB      0.0 MiB         101           for i in range(m):
    32     41.4 MiB      0.0 MiB       10100               for j in range(n):
    33     41.4 MiB      0.0 MiB       10000                   pass


Filename: d:/vscode py/现代程设/week 8/decorate.py

Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    35     41.4 MiB     41.4 MiB           1       @profile
    36                                             def serilizer(self, ds):
    37                                                 '''
    38                                                 序列化大型数据结构
    39                                                 '''
    40     41.4 MiB      0.0 MiB           1           with open("ds.txt", "wb") as f:
    41     41.5 MiB      0.1 MiB           1               pickle.dump(ds, f)
```

### 8.4 tqdm

- 重写方法`Disaster.data_structure_generator`：

  ```python
  def data_structure_generator(self, m, n):
          '''
          生成大型数据结构
          '''
          ds = [[random.randint(0,100) for i in range(m)] for j in tqdm(range(n))]
          return ds
  ```

  ```python
  56%|██████████████████████████████████████████████▏                                    | 5567/10000 [00:56<00:40, 108.35it/s]
  ```

- 重写方法`Disaster.traverse`：

  ```python
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
  ```

  ```python
  79%|█████████████████████████████████████████████████████████▎               | 7850206/10000000 [00:04<00:01, 1643973.89it/s]
  ```

### 8.5 路径检查装饰器

```python
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
```

- 若路径不存在，提示"path do not exist, automatically create it for you"，并且自动创建对应文件夹。

- 实例化后使用方法`d.serilizer(ds, "D:\\vscode py\\现代程设\\week 8\\fake path\\")`

  ```
  path do not exist, automatically create it for you
  created successfully
  ```

<img src="https://s2.loli.net/2022/01/29/X5x69qY4QhZMpVm.png" alt="image-20211118230737763" style="zoom: 50%;" />

### 8.6 播放音乐装饰器

```python
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
```

### 8.7 包管理与main函数

```python
import random
import pickle
# from line_profiler import LineProfiler
from memory_profiler import profile
from tqdm import tqdm
import time
from functools import wraps
import os
from playsound import playsound

if __name__ == "__main__":
    d = Disaster()
    ds = d.data_structure_generator(10, 10)
    d.traverse(ds)
    d.serilizer(ds, "D:\\vscode py\\现代程设\\week 8\\fake path\\")
```

