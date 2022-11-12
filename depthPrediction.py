import os
import torch
import cv2
import numpy as np
from MiDaS.MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator

useCPU = False
md = None

def LoadModel():
    global md
    md = midasDepthEstimator(threadCount=8)

def GetDepth(img):
    if md == None:
        LoadModel()

    # Estimate depth
    colorDepth = md.estimateDepth(img)

	# Join the input image, the estiamted depth and the combined image
    img_out = colorDepth

    return img_out