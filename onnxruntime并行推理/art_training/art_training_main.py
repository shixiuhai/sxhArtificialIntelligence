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
    p=subprocess.Popen(saveCmd.split(),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate(timeout=6)
    if str(error)=="b''":
        return cv2.imdecode(np.frombuffer(output, dtype=np.uint8), cv2.IMREAD_COLOR)
    else:
        return np.array([])


    
# 添加新模型需要添加
class ArtTraining:
    """
    在这里添加多个模型
    """
    def __init__(self,queueSize=10) -> None:
        # 加载人头模型
        self.headModel=Detector(640,0.6,0.6,"model/head.onnx",nameList=["head"])
        # 创建人头模型生产者
        self.headProducer=RabbitMqProducer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange)
        # 创建人头模型队列
        self.headQueue=Queue(maxsize=queueSize)
        print("-----------人头检测模型加载成功-----------")
        
        # 加载吸烟模型
        self.smokeModel=Detector(640,0.6,0.6,"model/zju-smokingFace.onnx",nameList=["smoke"])
        # 创建吸烟模型生成者
        self.smokeProducer=RabbitMqProducer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange)
        # 创建吸烟模型生产者
        self.smokeQueue=Queue(maxsize=queueSize)
        print("-----------吸烟检测模型加载成功-----------")
    
    # 人头检测
    def headDetect(self):
        while True:
            # print(self.headQueue.qsize())
            item=self.headQueue.get()
            id=item["id"]
            checkType=item["checkType"]
            imgArray=item["imgArray"]
            if imgArray.size!=0:
                # 这里要重写
                res=self.headModel.detect_out(imgArray)
                print("人头数量%s"%len(res))
                # 这里要重写
                self.headProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                    'id':id,
                    'img':cv2img_to_base64(imgArray),
                    'checkType':checkType,
                    # 'objNumber':len(res),
                    'data':str(res)
                })
                # for i in range(len(res)):
                #         name = res[i]['name']
                #         confidence_result = res[i]['confidence']
                #         xmin = res[i]['xmin']
                #         ymin = res[i]['ymin']
                #         xmax = res[i]['xmax']
                #         ymax = res[i]['ymax']
                #         # 设置判断置信度对比和满足条件的type
                #         if confidence_result>=0.2:
                #             # print(name)
                #             # 转换为x,y,width,height
                #             x = int(xmin)
                #             y =  int(ymin)
                #             w =  int(xmax-xmin+1)
                #             h =  int(ymax-ymin+1)
                #             # 画框
                #             # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), thickness=3)
                #             cv2.rectangle(imgArray, (x, y), (x + w, y + h), (0, 0, 255), thickness=2)
                #             # 添加概率值
                #             # cv2.putText(frame,"%s %.2s%%"%(name,confidence_result*100),(x+w+5,y-5),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
                #             cv2.putText(imgArray,"%s %.2s%%"%(name,confidence_result*100),(x+w+5,y-5),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
                # cv2.imwrite("10.png",imgArray)
                # break
            else:
                # 这里要重写
                self.headProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                    'id':id,
                    'img':'',
                    'checkType':checkType,
                    # 'objNumber':len(res),
                    'data':str(res)
                })
            
    # 吸烟检测
    def smokeDetect(self):
        while True:
            # print(self.smokeQueue.qsize())
            item=self.smokeQueue.get()
            id=item["id"]
            checkType=item["checkType"]
            imgArray=item["imgArray"]
            # return self.headModel.detect_out(image=imgArray)
            if imgArray.size!=0:
                # 这里要重写
                res=self.smokeModel.detect_out(imgArray)
                # print(res)
                # 这里要重写
                self.smokeProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                    'id':id,
                    'img':cv2img_to_base64(imgArray),
                    'checkType':checkType,
                    # 'objNumber':len(res),
                    'data':str(res)
                })
            else:
                # 这里要重写
                self.smokeProducer.send(queueName=monitoringWarningQueueName,routingKey=monitoringWarningKey,body={
                    'id':id,
                    'img':'',
                    'checkType':checkType,
                    # 'objNumber':len(res),
                    'data':str(res)
                })
           

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
        cv2.imwrite("source.png",imgArray)
        artTraining.headQueue.put({
            "id":id,
            "checkType":checkType,
            "imgArray":imgArray
        })
        # print("人头添加图片成功")
    
    if "smoke" in checkType:
        artTraining.smokeQueue.put({
            "id":id,
            "checkType":checkType,
            "imgArray":imgArray
        })
        # print("添加吸烟图片成功")

    
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
    
    # 创建一个进行截图的线程池
    threadPool = ThreadPoolExecutor(max_workers=15) 
    
    # 添加新模型需要添加
    # 定义一个检测类
    artTraining=ArtTraining()
    # 启动人头检测
    threading.Thread(target=artTraining.headDetect).start()
    # 启动吸烟检测
    threading.Thread(target=artTraining.smokeDetect).start()
    
    #image=imread_fast("2.png",channel_order='rgb')
    # image=cv2.imread("2.png")
    # print(artTraining.headDetect(image=image))
    RabbitMqConsumer(user=mqUser, pwd=mqPassword, host=mqHost, port=mqConnectPort,virtual_host=mqVirtualHost,exchange=mqExchange).receive(queueName=detectPhotoQueueName,routingKey=detectPhotoQueueKey,fun=callback)
    
    
    
    
    


