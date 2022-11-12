import cv2
import numpy as np
from MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator
import time

# Initialize depth estimation model
depthEstimator = midasDepthEstimator()

# Initialize webcam
camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cv2.namedWindow("Depth Image", cv2.WINDOW_NORMAL) 	

while True:
	startTime = time.time()
	# Read frame from the webcam
	ret, img = camera.read()

	# Estimate depth
	colorDepth = depthEstimator.estimateDepth(img)

	# Add the depth image over the color image:
	combinedImg = cv2.addWeighted(img,0.7,colorDepth,0.6,0)

	# Join the input image, the estiamted depth and the combined image
	img_out = np.hstack((img, colorDepth, combinedImg))

	cv2.imshow("Depth Image", img_out)

	# Press key q to stop
	if cv2.waitKey(1) == ord('q'):
		break

	print("FPS: " + str(1/(time.time() - startTime)) + "\r", end="")

camera.release()
cv2.destroyAllWindows()