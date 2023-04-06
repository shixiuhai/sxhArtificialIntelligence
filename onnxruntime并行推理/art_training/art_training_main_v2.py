import sys
import cv2
import numpy as np
import base64
from PIL import Image
import threading
import json
# yolov5导出模型
# python export.py --weights path/to/weights.pt --img 640 --batch 1
# image=np.array()
# 添加环境mixed_model
sys.path.append("mixed_model")
# 添加环境rabbitMq
sys.path.append("rabbitMq")
# 添加环境art_training
sys.path.append("log")
# from rabbitMq.ClassModelV3 import RabbitMqConsumer
# from rabbitMq.ClassModelV4 import RabbitMqProducer
from  rabbitMq.ClassModelV3 import RabbitMqConsumer,RabbitMqProducer
from log.ClassModel import Log
from log.ClassModel_timeInterval import Log as Log_timeInterval
from mixed_model.onnx_ort import Detector
from settings.config import *
import subprocess
# 创建一个5个线程的消费
from concurrent.futures import ThreadPoolExecutor
import queue
from queue import Queue
class ThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        # 队列大小为最大线程数的两倍
        self._work_queue = queue.Queue(self._max_workers * 2)
        
def cv2img_to_base64(cv2imgNp):
    # img = cv2.imread('test.jpg')
    # _, im_arr = cv2.imencode('.jpg', img)  # im_arr: image in Numpy one-dim array format.
    # im_bytes = im_arr.tobytes()
    # return base64.b64encode(im_bytes)
    image = cv2.imencode('.jpg',cv2imgNp)[1]
    return str(base64.b64encode(image))[2:-1]

def screenshot(videoPath:str)->np.ndarray:
    """
    定义ffmpeg截图函数实现flv,m3u8以及rtsp的截图
    """
    #  ffmpeg -loglevel quiet  -i %s -r 1 -t 0.1 -f image2
    # flv 和 m3u8 截图
    if videoPath.startswith("http") or videoPath.startswith("https"):
        saveCmd = "ffmpeg -loglevel quiet  -i %s -r 1 -t 0.1 -f image2 -"%videoPath
    # rtsp 截图
    elif videoPath.startswith("rtsp"):
        saveCmd = "ffmpeg -loglevel quiet -rtsp_transport tcp  -i %s -vframes 1 -f image2 -"%videoPath
    else:
        return np.array([])
    p=subprocess.Popen(saveCmd.split(),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        p.wait(6)
    except subprocess.TimeoutExpired:
        p.kill()
    finally:
        output, error = p.communicate()
        if str(error)=="b''":
            return cv2.imdecode(np.frombuffer(output, dtype=np.uint8), cv2.IMREAD_COLOR)
        else:
            return np.array([])


    
# 添加新模型要添加
class ArtTraining:
    """
    在这里添加多个模型
    """
    def __init__(self) -> None:
        # 加载人头模型
        self.headModel=Detector(640,0.2,0.6,"model/head.onnx")
        print("-----------人头检测模型加载成功-----------")
        # 加载吸烟模型
        self.smokeModel=Detector(640,0.2,0.6,"model/zju-smokingFace.onnx")
        print("-----------吸烟检测模型加载成功-----------")
    def headDetect(self,imgArray):
        return self.headModel.detect_out(image=imgArray)
    def smokeDetect(self,imgArray):
        return self.smokeModel.detect_out(image=imgArray)

# 进行多线程截图
def screenshot_threads(id:str,path:str,checkType:str):
    """
    在这里添加多个模型检测
    :param id 视频流的id
    :param path 视频流链接
    :param check 视频流检测类型
    """
    imgArray=screenshot(path)
    consumerVideoQueue.put({
        "id":id,
        "checkType":checkType,
        "imgArray":imgArray
    })
    print("添加图片成功")
    
def detect():
    """
    从队列中消费截图进行模型推理
    """
    while True:
        print(consumerVideoQueue.qsize())
        item=consumerVideoQueue.get()
        id=item["id"]
        checkType=item["checkType"]
        imgArray=item["imgArray"]
        if "head" in checkType:
            if imgArray.size!=0:
                # 这里要重写
                res=artTraining.headDetect(imgArray)
                print(res)
                # 这里要重写
                producer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                    'id':id,
                    'img':cv2img_to_base64(imgArray),
                    'checkType':checkType,
                    'data':str(res)
                })
            else:
                # 这里要重写
                producer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                    'id':id,
                    'img':'',
                    'checkType':checkType,
                    'data':str(res)
                })
        
        if "smoke" in checkType:
            if imgArray.size!=0:
                # 这里要重写
                res=artTraining.smokeDetect(imgArray)
                # 这里要重写
                producer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                    'id':id,
                    'img':cv2img_to_base64(imgArray),
                    'checkType':checkType,
                    'res':str(res)
                })
            else:
                # 这里要重写
                producer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                    'id':id,
                    'img':'',
                    'checkType':checkType,
                    'res':str(res)
                })
        
    

def callback(ch, method, properties, body):
        # 接收消息
        try:
            information=json.loads(body.decode(encoding='UTF-8'))
            id= information['id']
            path = information['path']
            checkType=information['checkType']
            # 通过线程池来调控线程数量和速度
            threadPool.submit(screenshot_threads,id,path,checkType)
            #detect(id=id,path=path,checkType=checkType)
            # 手动确认消费
            ch.basic_ack(delivery_tag=method.delivery_tag)
            # Thread(target=process_video_to_images,args=(path,save_path,companyId,taskId,anchorId,)).start()
            # MyThread(process_video_to_images,args=(path,save_path,companyId,taskId,anchorId,)).start()
        except Exception as error:
            log.error("callbak错误是：%s"%error)
        finally:
            return
        

if __name__ == "__main__":
    """
    定义检测使用的 线程池大小，
    定义每种模型的生产者，
    定义所有视频流的消费者，
    定义日志生产者
    """
    # 创建一个log对象
    log=Log(__name__, 'art_training_main.log').Logger
    log_timeInterval=Log_timeInterval("log2", '/home/wenhua/python/log/record.log').Logger
    # 创建一个接收线程池
    threadPool = ThreadPoolExecutor(max_workers=20) 
    # 创建一个队列
    consumerVideoQueue=Queue(maxsize=10)
    # 定义一个检测类
    artTraining=ArtTraining()
    # 定义检测结果发送的生产者
    producer=RabbitMqProducer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange)
    # 启动检测模型消费
    threading.Thread(target=detect).start()
    #image=imread_fast("2.png",channel_order='rgb')
    # image=cv2.imread("2.png")
    # print(artTraining.headDetect(image=image))
    RabbitMqConsumer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange).receive(queueName=detectPhotoQueueName,routingKey=detectPhotoQueueKey,fun=callback)
    
    
    
    
    


