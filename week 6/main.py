from PIL import Image
from PIL import ImageFilter
import os
import matplotlib.pyplot as plt

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

class TestImageShop(ImageShop):
    pass

def main():
    tis = TestImageShop()
    tis.load_images(suffix="jpg", path="D:\\vscode py\\现代程设\\week 6\\original images\\")
    tis.batch_ps(blur=8, resize=(400, 400))
    tis.display(nrow=3, ncol=3)
    tis.save(suffix="png", path="D:\\vscode py\\现代程设\\week 6\\modified images")

if __name__ == '__main__':
    main()