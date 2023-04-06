#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''=================================================
@File   :object_detect.py
@IDE    :vscode
@Author :yizhi
@Date   :2023/3/23
@Desc   :用onnxruntime部署yolov5
=================================================='''
import sys
sys.path.append("..")
from onnx_ort import Detector
from abc import ABCMeta,abstractclassmethod
# 定义一个实现目标检测类的接口
class ObjectDetect:
    def __init__(self) -> None:
        pass









# class ObjectDetect(metaclass=ABCMeta):
#     """
#     封装了基于onnx的多模型检测方案
#     """
#     # 初始化
#     def __init__(self) -> None:
#         pass
    
#     # 推理结果
#     @abstractclassmethod
#     def interence(self):
#         pass
    



