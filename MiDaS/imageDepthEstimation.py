import cv2
import numpy as np
from MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator

imagePath = "img/image.jpg"

# Initialize depth estimation model
depthEstimator = midasDepthEstimator()

# Read RGB images
img = cv2.imread(imagePath, cv2.IMREAD_COLOR)

# Estimate depth
colorDepth = depthEstimator.estimateDepth(img)

# Add the depth image over the color image:
combinedImg = cv2.addWeighted(img,0.7,colorDepth,0.6,0)

# Join the input image, the estiamted depth and the combined image
img_out = np.hstack((img, colorDepth, combinedImg))

# Draw estimated depth
cv2.namedWindow("Depth Image", cv2.WINDOW_NORMAL) 
cv2.imshow("Depth Image", img_out)
cv2.waitKey(0)

cv2.imwrite("output.jpg",img_out)
