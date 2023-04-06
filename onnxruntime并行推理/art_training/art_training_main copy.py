import sys
import cv2
import numpy as np
from PIL import Image
# yolov5导出模型
# python export.py --weights path/to/weights.pt --img 640 --batch 1
# image=np.array()
# 为mixed_model添加环境
sys.path.append("mixed_model")
# 为rabbitMq添加环境
sys.path.append("rabbitMq")
# from rabbitMq.ClassModelV3 import RabbitMqConsumer
# from rabbitMq.ClassModelV4 import RabbitMqProducer
from  rabbitMq.ClassModelV3 import RabbitMqProducer,RabbitMqConsumer
from mixed_model.onnx_ort import Detector
from settings.config import *
# 创建一个5个线程的消费
from concurrent.futures import ThreadPoolExecutor
import queue
class ThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        # 队列大小为最大线程数的两倍
        self._work_queue = queue.Queue(self._max_workers * 2)
threadPool = ThreadPoolExecutor(max_workers=5) 

def imread_fast(path, channel_order='bgr'):
    """
    使用 Pillow 和 numpy 实现的更快图像读取函数
    :param path: 图像文件路径
    :param channel_order: 通道顺序，'bgr' 或 'rgb'
    :return: 图像数组
    """
    # 使用 Pillow 打开图像文件
    with Image.open(path) as img:
        # 将图像转换为 numpy 数组
        img_array = np.array(img)

        # 如果是灰度图像，则直接返回
        if len(img_array.shape) == 2:
            return img_array

        # 如果是彩色图像
        elif len(img_array.shape) == 3 and img_array.shape[2] == 3:
            # 调整通道顺序
            if channel_order == 'rgb':
                img_array = img_array[:, :, ::-1]  # RGB to BGR
            # 将颜色通道从第三个维度移动到第一个维度
            img_array = np.moveaxis(img_array, 2, 0)

            # 将图像数据类型转换回来
            img_array = img_array.astype(np.uint8)

            return img_array

        # 其他情况，抛出异常
        else:
            raise ValueError("Unsupported image shape: {}".format(img_array.shape))


        
class ArtTraining:
    def __init__(self) -> None:
        # 加载人头模型
        self.headModel=Detector(640,0.2,0.6,"model/head.onnx")
        print("-----------人头检测模型加载成功-----------")
        # 加载吸烟模型
        self.smokeModel=Detector(640,0.2,0.6,"model/zju-smokingFace.onnx")
        print("-----------吸烟检测模型加载成功-----------")
    def headDetect(self,image):
        return self.headModel.detect_out(image=image)
    def smokeDetect(self,image):
        return self.smokeModel.detect_out(image=image)
    
def detect(type:str,image:np.array):
    pass
if __name__ == "__main__":
    # 定义一个检测类
    artTraining=ArtTraining()
    #image=imread_fast("2.png",channel_order='rgb')
    image=cv2.imread("2.png")
    print(artTraining.headDetect(image=image))
    
    
    
    


