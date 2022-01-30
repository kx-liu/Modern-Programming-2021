## Week 1: Hello Python

1. 搭建python开发环境并确定开发IDE（无需提交）

2. 用pip或anaconda管理包，配置开发环境：（无需提交）

- 基础功能或技巧：
    virtualenv：或者直接使用conda的虚拟环境
    tdqm：进度条，训练或者数据加载非常有用
    json/demjson：大部分数据以json格式存储，部分不标准的json文本需要利用demjson
    pickle： 结果序列化存储
    argparse：交互参数解析

- 数据处理基础：
    numpy：数组，
    scipy
    pandas

- 可视化：
    matplotlib：最常用的绘图工具
    seaborn：辅助matplotlib使用
    forlium/pyecharts(python中只推荐地图绘图部分，建议利用原生的js配合系统开发库实现功能更多的图)

- 爬虫：
    requests/urllib:发出基本的网络请求
    BeautifulSoup:主要功能是html内容的解析
    Scrapy：基本的爬虫与数据采集
    Selenium：模拟浏览器访问，和Scrapy等配合使用

- 文本处理：
    jieba：分词工具
    gensim:话题模型及word2vec嵌入等

- 图/网络数据：
    networkx：复杂网络分析

- 图片处理初步：
    pillow(PIL):图片的基本变换，深度学习部分要用到图片数据
    opencv-python:图片+视频数据

- 音频处理初步：
    librosa

- 统计模型：
    statsmodels