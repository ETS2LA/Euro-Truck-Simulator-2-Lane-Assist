import cv2
import numpy as np
from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.utils import LaneModelType
from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.ultrafastLaneDetector import UltrafastLaneDetector
from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.ultrafastLaneDetectorV2 import UltrafastLaneDetectorV2

if __name__ == "__main__":
	image_path = "./temp/test3.jpg"
	model_path = "plugins/UFLDLaneDetection/UFLD/models/tusimple_res34.onnx"
	# model_type = LaneModelType.UFLD_TUSIMPLE
	model_type = LaneModelType.UFLDV2_CULANE


	# Initialize lane detection model
	# Initialize lane detection model
	print("Model Type : ", model_type.name)
	if ( "UFLDV2" in model_type.name) :
		lane_detector = UltrafastLaneDetectorV2(model_path, model_type)
	else :
		lane_detector = UltrafastLaneDetector(model_path, model_type)

	# Read RGB images
	img = cv2.imread(image_path, cv2.IMREAD_COLOR)
	if img is None:
		print("The picture path [%s] can't not found!" % (image_path) )
		exit()
	else :
		# Detect the lanes
		output_img = lane_detector.AutoDrawLanes(img)

		# Draw estimated depth
		# cv2.namedWindow("Detected lanes", cv2.WINDOW_NORMAL) 
		cv2.imshow("Detected lanes", output_img)
		cv2.waitKey(0)

		cv2.imwrite("output.jpg",output_img)

