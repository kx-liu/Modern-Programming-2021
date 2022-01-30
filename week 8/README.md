## Week 8: Decorator

当进行大批量数据读取、模型训练等，往往需要花费大量时间。这类耗时长的程序有一些通用的功能需求，可以通过装饰器实现，具体如下：

1. 实现一个类，在其中提供一些方法模拟耗时耗内存的一些操作，以测试如下的装饰器（用类或函数实现），如大的数据结构生成、遍历、写入文件序列化等。

2. 如果需要知道程序的运行时间、运行进度、内存占用情况，请利用line_profiler、memory_profiler、tqdm等装饰器实现相关功能，要求在程序执行结束后，打印程序的内存占用和运行时间。

3. 在程序处理结束后，通常需要将模型或者数据处理结果保存下来。但是，有时会因为路径设置错误（忘记新建文件夹）等原因导致文件无法存储，浪费大量的时间重复运行程序。一种解决方法是在执行程序前对参数中的路径进行检查。要求利用装饰器函数实现这一功能，接收函数的路径参数，检查路径对应文件夹是否存在，若不存在，则给出提示，并在提示后由系统自动创建对应的文件夹。

4. 在程序运行结束后，可以给用户发送一个通知，比如播放一段音乐等。要求实现对应的装饰器类，在被装饰的函数执行结束后，可以主动播放声音（了解并使用一下playsound或其他声音文件处理的库）。