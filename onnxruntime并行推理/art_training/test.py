import subprocess
import cv2
import numpy as np

import sys
sys.path.append("mixed_model")
# 添加环境rabbitMq
sys.path.append("rabbitMq")
# 添加环境art_training
sys.path.append("log")
from mixed_model.onnx_ort import Detector

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
    def headDetect(self,image):
        return self.headModel.detect_out(image=image)
    def smokeDetect(self,image):
        return self.smokeModel.detect_out(image=image)

def screenshot(videoPath:str)->np.ndarray:
    """
    定义ffmpeg截图函数实现flv,m3u8以及rtsp的截图
    """
    #  ffmpeg -loglevel quiet  -i %s -r 1 -t 0.1 -f image2
    if videoPath.startswith("http") or videoPath.startswith("https"):
        saveCmd = "ffmpeg -loglevel quiet  -i %s -r 1 -t 0.1 -f image2 -"%videoPath
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
            

if __name__ == '__main__':
    img=screenshot("http://pili-live-hdl.qingyajiu.com/live/2673a668685d21e1d1851f6617779540.flv")
    img=screenshot("rtsp://video.hzxinyule.com:6006/live/0eee27d235b949d3a957275e1df082f7_1_1")
    print(img)
    # print(img.size)
    artTraining=ArtTraining()
    if img.size!=0:
        print(artTraining.headDetect(image=img))
  
    
    
