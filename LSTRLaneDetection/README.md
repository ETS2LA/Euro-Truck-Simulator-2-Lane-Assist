# ONNX LSTR Lane Detection
Python scripts for performing lane detection using the Lane Shape Prediction with Transformers (LSTR) model in ONNX.

![ONNX LSTR Lane Detection](https://github.com/ibaiGorordo/ONNX-LSTR-Lane-Detection/blob/main/doc/img/lane_Detection.jpg)

# Requirements

 * Check the requirements.txt file. Additionally, **pafy** and **youtube-dl** are required for youtube video inference. 
 
# Installation
```
pip install -r requirements.txt
pip install pafy youtube-dl
```

# ONNX model
The original model was converted to different formats (including .onnx) by [PINTO0309](https://github.com/PINTO0309), the models can be found in [his repository](https://github.com/PINTO0309/PINTO_model_zoo/tree/main/167_LSTR).

# Original Pytorch model
The pretrained Pytorch model was taken from the [original repository](https://github.com/liuruijin17/LSTR).

# Examples

 * **Image inference**:
 
 ```
 python image_lane_detection.py
 ```
 
  * **Video inference**:
 
 ```
 python video_lane_detection.py
 ```
 
 # [Inference video Example](https://youtu.be/9pfrol-mEWo) 
 ![!ONNX LSTR Lane Detection on video](https://github.com/ibaiGorordo/ONNX-LSTR-Lane-Detection/blob/main/doc/img/lane_detection.gif)
 
 Original video: https://youtu.be/2CIxM7x-Clc (by Yunfei Guo)
