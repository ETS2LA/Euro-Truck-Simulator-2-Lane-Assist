import cv2
import pafy
import numpy as np
from MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator

videoUrl = 'https://youtu.be/TGadVbd-C-E'
videoPafy = pafy.new(videoUrl)

# Initialize depth estimation model
depthEstimator = midasDepthEstimator()

# Initialize video
# cap = cv2.VideoCapture("img/test.mp4")
print(videoPafy.streams)
cap = cv2.VideoCapture(videoPafy.streams[-1].url)
cv2.namedWindow("Depth Image", cv2.WINDOW_NORMAL) 	

while cap.isOpened():

	# Read frame from the video
	ret, img = cap.read()

	if ret:	

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

cap.release()
cv2.destroyAllWindows()
