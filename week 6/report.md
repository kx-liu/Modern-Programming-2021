## 第六次作业 类继承——图片的简单处理

### 6.1 大致框架

```python
class Filter:
    '''
    data_attr: 待处理的图片实例；参数列表，用以存储可能使用参数的滤波器的参数
    '''
    def __init__(self, radius=None, size=None):
        pass
    def filter(self):
        pass

# 以下四类为Filter子类，以实现Filter类中的filter功能，返回修改后的图片列表
class FindEdges(Filter):
    def filter(self, images_list):
        return modified_images

class Sharpen(Filter):
    def filter(self, images_list):
        return modified_images

class Blur(Filter):
    def filter(self, images_list):
        return modified_images

class Resize(Filter):
    def filter(self, images_list):
        return modified_images

class ImageShop:
    '''
    data_attr: 图片格式，图片文件，存储图片实例的列表，存储处理过的图片
    '''
    def __init__(self):
        pass
    def load_images(self, suffix, path):
        '''
        从路径加载特定格式的图片
        '''
        pass
    def batch_ps(self, **argv):
        '''
        输入对图片的操作，格式如下：
        findedges=None | sharpen=None | blur=radius | resize=(length, width)
        对外方法
        '''
        ImageShop.__batch_ps(self)
    def __batch_ps(self):
        '''
        内部方法，调用以上4个Filter子类以处理图片
        '''
        pass
    def display(self, nrow, ncol):
        '''
        处理效果显示
        '''
    def save(self, suffix, path):
        '''
        处理结果输出
        '''

class TestImageShop(ImageShop):
    '''
    ImageShop的继承，用于Imageshop的实例化测试。
    '''
    pass
```

### 6.2 Filter类

```python
class Filter:
    def __init__(self, radius=None, size=None):
        params = []
        params.append(radius)
        params.append(size)
        self.radius = radius
        self.size = size
        self.images_list = []

    def filter(self):
        pass
```

- `params`以保存可能使用参数的滤波器的参数，其中有
  - `radius`，即`GaussianBlur`的参数
  - `size`，即`resize`的参数

- `filter`方法的具体细节交给以下四个`Filter`子类

### 6.3 Filter子类

```python
class FindEdges(Filter):
    def filter(self, images_list):
        modified_images = []
        for image in images_list:
            image_edge = image.filter(ImageFilter.FIND_EDGES)
            modified_images.append(image_edge)
        return modified_images

class Sharpen(Filter):
    def filter(self, images_list):
        modified_images = []
        for image in images_list:
            image_sharpen = image.filter(ImageFilter.SHARPEN)
            modified_images.append(image_sharpen)
            # image_sharpen_2 = image_sharpen.filter(ImageFilter.SHARPEN)
        return modified_images

class Blur(Filter):
    def filter(self, images_list):
        modified_images = []
        for image in images_list:
            image_blur = image.filter(ImageFilter.GaussianBlur(radius=self.radius))
            modified_images.append(image_blur)
        return modified_images

class Resize(Filter):
    def filter(self, images_list):
        modified_images = []
        for image in images_list:
            image_resize = image.resize(self.size)
            modified_images.append(image_resize)
        return modified_images
```

- 四个子类中分别只有一个方法`filter`以实现基类的`filter`方法，接受参数为`images_list`，即`PIL.Imgae.open()`后的`PIL`实例列表；
- 经过分别四类的处理后生成`modified_images`。

### 6.4 ImageShop类

```python
class ImageShop:
    def __init__(self):
        pass

    def load_images(self, suffix, path):
        self.suffix = suffix
        self.path = path
        images_name = []
        images_list = []
        file_list = os.listdir(path)
        for file in file_list:
            ls = file.split(".")
            if suffix in ls[1].lower():
                images_name.append(ls[0])
                images_list.append(Image.open(path+"\\"+file))
        self.images_list = images_list
        self.images_name = images_name

    def batch_ps(self, **argv):
        '''
        输入对图片的操作，格式如下：
        findedges=None | sharpen=None | blur=radius | resize=(length, width)
        '''
        _operations = []
        for key in argv.keys():
            if key == "findedges":
                fe = FindEdges()
                _operations.append(fe)
            elif key == "sharpen":
                sh = Sharpen()
                _operations.append(sh)
            elif key == "blur":
                bl = Blur(radius=argv[key])
                _operations.append(bl)
            elif key == "resize":
                rs = Resize(size=argv[key])
                _operations.append(rs)
            else:
                print(f"We have no {key!r} operation.")
        self._operations = _operations
        ImageShop.__batch_ps(self)

    def __batch_ps(self):
        images_list = self.images_list
        _operations = self._operations
        for operation in _operations:
            images_list = operation.filter(images_list)
        self.__modified_images = images_list

    def display(self, nrow, ncol):
        for i in range(len(self.__modified_images)):
            if i == nrow * ncol: break
            plt.subplot(nrow, ncol, i+1)
            plt.imshow(self.__modified_images[i])
            plt.axis("off")
        plt.show()

    def save(self, suffix, path):
        if os.path.exists(path) == False:
            os.mkdir(path)
        assert len(self.images_name) == len(self.__modified_images)
        for i in range(len(self.images_name)):
            self.__modified_images[i].save(path+"\\"+self.images_name[i]+"."+suffix)
```

#### 6.4.1 ImageShop.load_images

- 用户提供想要批量处理的图片格式`suffix`，以及导入图片的地址`path`，通过`load_images`方法将对应照片文件用`PIL`打开，并存入`images_list`内，同时获取文件名列表`images_name`。

#### 6.4.2 ImageShop.batch_ps

- 用户输入对图片做何处理，同时附加对应参数，如做锐化与调整大小为(400,400)的处理，则调用方法`batch_ps(sharpen=None, resize=(400,400))`，由不定长参数`**argv`的方法来实现；
- 将需要进行的操作对应`Filter`子类实例化，存入`_operations`列表中；
- 调用`__batch_ps`内部方法，以实现对图片的具体操作。

#### 6.4.3 ImageShop.__batch_ps

- 调用`Filter`子类以实现对图片的具体操作，将处理后的图片存入`__modified_images`列表中。

#### 6.4.4 ImageShop.display

- 用户输入要展示的行列数`nrow, ncol`，这里认为最大输出图片数量即为`nrow * ncol`，若处理后的照片书大于最大输出图片数量，则仅输出最大输出图片数量张图片；

#### 6.4.5 ImageShop.save

- 用户提供保存图片格式与保存路径，将图片转化格式后输出至对应路径。

### 6.5 TestImageShop类

```python
class TestImageShop(ImageShop):
    pass
```

- 为简化问题，将其设为`ImageShop`的子类。

### 6.6 main函数与包管理

```python
from PIL import Image
from PIL import ImageFilter
import os
import matplotlib.pyplot as plt

def main():
    tis = TestImageShop()
    tis.load_images(suffix="jpg", path="D:\\vscode py\\现代程设\\week 6\\original images\\")
    tis.batch_ps(blur=8, resize=(400, 400))
    tis.display(nrow=3, ncol=3)
    tis.save(suffix="png", path="D:\\vscode py\\现代程设\\week 6\\modified images")

if __name__ == '__main__':
    main()
```

### 6.7 效果展示

- original images

<img src="https://s2.loli.net/2022/01/29/pgMJUCNsxDbuO8l.png" alt="image-20211026201421720" style="zoom: 33%;" />

- modified images

<img src="https://s2.loli.net/2022/01/29/8lkZGoe4aN3xbyc.png" alt="image-20211026201532459" style="zoom:33%;" />

<img src="https://s2.loli.net/2022/01/29/G1kcfBh3e69DuLE.png" alt="image-20211026201626480" style="zoom:33%;" />
