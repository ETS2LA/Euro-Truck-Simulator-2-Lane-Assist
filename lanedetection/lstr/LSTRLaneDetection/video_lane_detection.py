from enum import Enum
import cv2
import pafy
from lstr import LSTR
import time

class ModelType(Enum):
    LSTR_180X320 = "lstr_180x320"
    LSTR_240X320 = "lstr_240x320"
    LSTR_360X640 = "lstr_360x640"
    LSTR_480X640 = "lstr_480x640"
    LSTR_720X1280 = "lstr_720x1280"

model_type = ModelType.LSTR_360X640
model_path = f"models/{model_type.value}.onnx"

# Initialize video
# cap = cv2.VideoCapture("video.mp4")
videoUrl = "https://www.youtube.com/watch?v=O5XZWLT4FAo"
videoPafy = pafy.new(videoUrl)
print(videoPafy.streams)
cap = cv2.VideoCapture(videoPafy.streams[-1].url)

# Initialize lane detection model
lane_detector = LSTR(model_type, model_path)

cv2.namedWindow("Detected lanes", cv2.WINDOW_NORMAL)	

# out = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 20, (1280,720))

ret = None
frame = None
while cap.isOpened():
	startTime = time.time()
	try:
		# Read frame from the video
		ret, frame = cap.read()
	except:
		continue

	if ret != None:	

		# Detect the lanes
		detected_lanes, lane_ids = lane_detector.detect_lanes(frame)
		output_img = lane_detector.draw_lanes(frame)

		cv2.imshow("Detected lanes", output_img)
		# out.write(output_img)

	else:
		break

	print(f"FPS: {1/(time.time()-startTime)}\r", end="")
	# Press key q to stop
	if cv2.waitKey(1) == ord('q'):
		break

cap.release()
# out.release()
cv2.destroyAllWindows()