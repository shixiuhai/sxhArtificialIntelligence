import cv2
from onnx_ort import Detector
image = cv2.imread("2.png")
# print(image)
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import queue
import subprocess
import copy
# 创建一个5个线程的消费
class ThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        # 队列大小为最大线程数的两倍
        self._work_queue = queue.Queue(self._max_workers * 2)

threadPool = ThreadPoolExecutor(max_workers=4) 
obj=Detector(640,0.2,0.6,"zju-smokingFace.onnx")
obj1=Detector(640,0.2,0.6,"zju-smokingFace.onnx")
obj2=Detector(640,0.2,0.6,"zju-smokingFace.onnx")
obj3=Detector(640,0.2,0.6,"zju-smokingFace.onnx")
obj4=Detector(640,0.2,0.6,"zju-smokingFace.onnx")
start=time.time()
def job():
    obj.detect_out(image)
def job1():
    obj1.detect_out(image)
def job2():
    obj2.detect_out(image)
def job3():
    obj3.detect_out(image)
    #print(obj.detect_out(image))

pool=ThreadPoolExecutor(max_workers=4)
for i in range(1000):
    # job(obj)
    job1()
end=time.time()
print("耗费时间是%s"%(end-start))
# print(det.detect_out(image))
# print(det.detect_out(image))
# print(det.detect_out(image))
# print(det.detect_out(image))


