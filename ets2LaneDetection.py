import cv2
import time
from mss import mss
import numpy as np
from PIL import Image
from torch import fake_quantize_per_tensor_affine
from ultrafastLaneDetector import UltrafastLaneDetector, ModelType


model_path = "models/culane_18.pth"
model_type = ModelType.CULANE

# Initialize lane detection model
try:
    lane_detector = UltrafastLaneDetector(model_path, model_type, use_gpu=False)
    lane_detector.modelSize = "18"
except:
    print("Default model not installed, please select one in the settings")


# Set the default variables for the screenshot
w, h = 833, 480
x, y = 500, 200
sct = mss()
monitor = {'top': y, 'left': x, 'width': w, 'height': h}
steeringOffset = -150
showPreview = True
close = False

def ChangeModel(model, useGPU):
    global lane_detector
    global model_type

    if "culane" in model:
        model_type = ModelType.CULANE
    elif "tusimple" in model:
        model_type = ModelType.TUSIMPLE
    modelDepth = "18"

    if "34" in model:
        modelDepth = "34"
    elif "101" in model:
        modelDepth = "101"

    lane_detector = UltrafastLaneDetector("models/" + model, model_type, use_gpu=useGPU.get(), modelDepth = modelDepth)


def ChangeVideoDimension(value, value2):
    global w
    global h
    global x
    global y
    global monitor
    value[0] = int(value[0])
    value[1] = int(value[1])
    value2[0] = int(value2[0])
    value2[1] = int(value2[1])
    w = value[0]
    h = value[1]
    x,y = value2
    monitor = {'top': y, 'left': x, 'width': w, 'height': h}
    print(monitor)

def ChangeLaneAssist(value):
    global steeringOffset
    steeringOffset = value


cv2.namedWindow("Detected lanes", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Detected lanes", w, h)
cv2.setWindowProperty("Detected lanes", cv2.WND_PROP_TOPMOST, 1)
difference = 0
fps = 0
def UpdateLanes(drawCircles):
    global difference
    global fps
    
    startTime = time.time_ns()
    frame = np.array(Image.frombytes('RGB', (w,h), sct.grab(monitor).rgb))
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    # Detect the lanes
    output_img = lane_detector.detect_lanes(frame, drawCircles)
    try:
        difference = (lane_detector.lanes_points[1][0][0] + lane_detector.lanes_points[2][0][0]) / 2
        difference = difference - (w / 2)
        difference = difference + steeringOffset
    except Exception as ex:
        pass
    lane1Points = None
    lane2Points = None
    drivingPoints = None
    try:
        lane1Points = []
        lane2Points = []
        drivingPoints = []
        for lane_num,lane_points in enumerate(lane_detector.lanes_points):
            for lane_point in lane_points:
                if(lane_num == 1):
                    lane1Points.append(lane_point)
                elif(lane_num == 2):
                    lane2Points.append(lane_point)
        if(len(lane1Points) > len(lane2Points)):
            for i in range(len(lane2Points)):
                if i % 10 != 0:
                    continue
                if(lane1Points[i][0] != 0):
                    cv2.circle(output_img, (int((lane1Points[i][0] + lane2Points[i][0]) / 2), lane1Points[i][1]), 5, (0, 255, 0), -1)
                    drivingPoints.append((int((lane1Points[i][0] + lane2Points[i][0]) / 2), lane1Points[i][1]))
        else:
            for i in range(len(lane1Points)):
                if i % 10 != 0:
                    continue
                if(lane1Points[i][0] != 0):
                    cv2.circle(output_img, (int((lane1Points[i][0] + lane2Points[i][0]) / 2), lane1Points[i][1]), 5, (0, 255, 0), -1)
                    drivingPoints.append((int((lane1Points[i][0] + lane2Points[i][0]) / 2), lane1Points[i][1]))
    except Exception as ex:
        pass
    
    try:
        cv2.line(output_img, (int(w/2 + steeringOffset), drivingPoints[0][1]), (drivingPoints[0][0], drivingPoints[0][1]), (0, 0, 255), 2)
    except:
        pass
    endTime = time.time_ns()
    fps = 1000000000 / (endTime - startTime)
    cv2.putText(output_img, "FPS : " + str(round(fps, 1)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    if(showPreview):
        cv2.imshow("Detected lanes", output_img)
    else:
        cv2.destroyAllWindows()
    if cv2.waitKey(1) & 0xFF == ord('q') or close:
        exit()

