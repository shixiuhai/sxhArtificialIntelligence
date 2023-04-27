import sys
import cv2
import numpy as np
import base64
from PIL import Image
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
import time
# from queue import Queue
from multiprocessing import Queue,Process
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
    image = cv2.imencode('.jpeg',cv2imgNp)[1]
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
    try:
        p = subprocess.Popen(saveCmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate(timeout=6)
        if output:
            p.kill()
            return cv2.imdecode(np.frombuffer(output, dtype=np.uint8), cv2.IMREAD_COLOR)
        else:
            p.kill()
            return np.array([])
    except Exception as error:
        log.error("截图错误是%s"%error)
        p.kill()
        return np.array([])
    

# 添加新模型需要添加
# 进行多线程截图
def screenshot_threads(id:str,path:str,checkType:str):
    """
    在这里添加多个模型检测
    :param id 视频流的id
    :param path 视频流链接
    :param check 视频流检测类型
    """
    imgArray=screenshot(path)
    if "head" in checkType:
        # print("添加人头成功")
        headQueue.put({
            "id":id,
            "checkType":"head",
            "imgArray":imgArray
        })
        # headQueue.get()
    
    if "smoke" in checkType:
        # print("添加吸烟目标成功")
        smokeQueue.put({
            "id":id,
            "checkType":"smoke",
            "imgArray":imgArray
        })
        # smokeQueue.get()
    
    if "fire" in checkType:
        fireQueue.put({
            "id":id,
            "checkType":"fire",
            "imgArray":imgArray
        })

# 添加新模型需要添加
class ArtTrainingProcess:
    """
    在这里添加多个模型
    """
    def __init__(self) -> None:
        print("---------开始启动多模型检测---------")
    # 人头检测
    @staticmethod
    def headDetect():
        headModel=Detector(640,0.6,0.6,"model/head.onnx",nameList=["head"])
        headProducer=RabbitMqProducer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange)
        count=0
        countMax=100
        print("---------艺术培训人头检测模型启动成功---------")
        log.info("---------艺术培训人头检测模型启动成功---------")
        while True:
            if count>countMax:
                count=0
                print("人头检测队列大小"+str(headQueue.qsize()))
                log.info("人头检测队列大小"+str(headQueue.qsize()))
            try:
                if headQueue.qsize()>=1:
                    count=count+1
                    item=headQueue.get()
                    id=item["id"]
                    checkType=item["checkType"]
                    imgArray=item["imgArray"]
                    if imgArray.size!=0:
                        # print("人头检测成功")
                        # 这里要重写
                        res=headModel.detect_out(imgArray)
                        # print("--------------人头检测成功")
                        if res!=[]:
                            print("检测到人头数量是%s"%len(res))
                            # 这里要重写
                            headProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':str(res),
                                'img':cv2img_to_base64(imgArray)
                            })
                        else:
                            # 这里要重写
                            headProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':str(res),
                                'img':''
                            })
                    else:
                        headProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':"[]",
                                'img':''
                            })
                else:
                    # 队列目标数量小于某个量级后进行等待队列添加
                    time.sleep(0.1)
            except Exception as error:
                log.error("代码167行,人头检测出现错误,错误是%s"%error)
                
    # 吸烟检测
    @staticmethod
    def smokeDetect():
        smokeModel=Detector(640,0.6,0.6,"model/zju-smokingFace.onnx",nameList=["smoke"])
        smokeProducer=RabbitMqProducer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange)
        count=0
        countMax=100
        print("---------场所吸烟检测模型启动成功---------")
        log.info("---------场所吸烟检测模型启动成功---------")
        while True:
            if count>countMax:
                count=0
                print("吸烟检测队列大小"+str(smokeQueue.qsize()))
                log.info("吸烟检测队列大小"+str(smokeQueue.qsize()))
            try:
                if smokeQueue.qsize()>=1:
                    count=count+1
                    item=smokeQueue.get()
                    id=item["id"]
                    checkType=item["checkType"]
                    imgArray=item["imgArray"]
                    # 成功截图
                    if imgArray.size!=0:
                        # print("吸烟检测成功")
                        # 这里要重写
                        res=smokeModel.detect_out(imgArray)
                        if res!=[]:
                            # 这里要重写
                            smokeProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':str(res),
                                'img':cv2img_to_base64(imgArray)
                            })
                        else:
                            # 这里要重写
                            smokeProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':str(res),
                                'img':''
                            })
                    # 没有成功截图
                    else:
                        smokeProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':"[]",
                                'img':''
                            })
                else:
                    # 队列目标数量小于某个量级后进行等待队列添加
                    time.sleep(0.1)
            
            except Exception as error:
                log.error("代码226行,吸烟检测出现错误,错误是%s"%error)

    # 火焰检测
    @staticmethod
    def fireDetect():
        fireModel=Detector(640,0.6,0.6,"model/fire.onnx",nameList=["fire"])
        fireProducer=RabbitMqProducer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange)
        count=0
        countMax=100
        print("---------场所火焰检测模型启动成功---------")
        log.info("---------场所火焰检测模型启动成功---------")
        while True:
            if count>countMax:
                count=0
                print("火焰检测队列大小"+str(fireQueue.qsize()))
                log.info("火焰检测队列大小"+str(fireQueue.qsize()))
            try:
                if fireQueue.qsize()>=1:
                    count=count+1
                    item=fireQueue.get()
                    id=item["id"]
                    checkType=item["checkType"]
                    imgArray=item["imgArray"]
                    # 成功截图
                    if imgArray.size!=0:
                        # print("吸烟检测成功")
                        # 这里要重写
                        res=fireModel.detect_out(imgArray)
                        # print("+++++++++吸烟检测成功")
                        if res!=[]:
                            # 这里要重写
                            fireProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':str(res),
                                'img':cv2img_to_base64(imgArray)
                            })
                        else:
                            # 这里要重写
                            fireProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':str(res),
                                'img':''
                            })
                    # 没有成功截图
                    else:
                        fireProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                                'id':id,
                                'checkType':checkType,
                                'data':"[]",
                                'img':''
                            })
                else:
                    # 队列目标数量小于某个量级后进行等待队列添加
                    time.sleep(0.1)
            
            except Exception as error:
                print(res)
                log.error("代码285行,火焰检测出现错误,错误是%s"%error)
    
    
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
    log=Log(__name__, 'model_training_main.log').Logger
    log_timeInterval=Log_timeInterval("log2", '/home/wenhua/python/log/record.log').Logger
    
    # 创建一个进行截图的线程池
    threadPool = ThreadPoolExecutor(max_workers=36) 
    
    # 添加新模型需要添加
    # 创建一个人头队列
    headQueue=Queue(maxsize=10)
    # 创建一个吸烟队列
    smokeQueue=Queue(maxsize=10)
    # 创建一个火焰检测队列
    fireQueue=Queue(maxsize=10)
    
    # 启动模型检测
    Process(target=ArtTrainingProcess.headDetect).start()
    time.sleep(2)
    # Process(target=ArtTrainingProcess.headDetect).start()
    Process(target=ArtTrainingProcess.smokeDetect).start()
    time.sleep(2)
    # Process(target=ArtTrainingProcess.smokeDetect).start()
    Process(target=ArtTrainingProcess.fireDetect).start()
    # Process(target=ArtTrainingProcess.fireDetect).start()

    
    # 启动任务消费
    RabbitMqConsumer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange).receive(queueName=detectPhotoQueueName,routingKey=detectPhotoQueueKey,fun=callback)
    
    
    


