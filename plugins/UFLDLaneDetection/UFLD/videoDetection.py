import cv2, time
# import pafy
from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.utils import LaneModelType
from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.ultrafastLaneDetector import UltrafastLaneDetector
from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.ultrafastLaneDetectorV2 import UltrafastLaneDetectorV2


video_path = "./temp/test.mp4"
model_path = "models/tusimple_18.onnx"
# model_type = LaneModelType.UFLD_TUSIMPLE
model_type = LaneModelType.UFLD_TUSIMPLE

if __name__ == "__main__":
	# Initialize video
	cap = cv2.VideoCapture(video_path)
	if not cap.isOpened():
		print("The video path [%s] can't not found!" % (video_path) )
		exit()
	width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float `width`
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

	# Initialize lane detection model
	print("Model Type : ", model_type.name)
	if ( "UFLDV2" in model_type.name) :
		lane_detector = UltrafastLaneDetectorV2(model_path, model_type)
	else :
		lane_detector = UltrafastLaneDetector(model_path, model_type)

	cv2.namedWindow("Detected lanes", cv2.WINDOW_NORMAL)	
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	vout = cv2.VideoWriter(video_path[:-4]+'_out.mp4', fourcc , 30.0, (width, height))
	fps = 0
	frame_count = 0
	start = time.time()
	while cap.isOpened():
		try:
			# Read frame from the video
			ret, frame = cap.read()
		except:
			continue

		if ret:	

			# Detect the lanes
			output_img = lane_detector.AutoDrawLanes(frame)

			frame_count += 1
			if frame_count >= 30:
				end = time.time()
				fps = frame_count / (end - start)
				frame_count = 0
				start = time.time()
			cv2.putText(output_img, "FPS: %.2f" % fps, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
			cv2.imshow("Detected lanes", output_img)

		else:
			break
		vout.write(output_img)	
		# Press key q to stop
		if cv2.waitKey(1) == ord('q'):
			break

	vout.release()
	cap.release()
	cv2.destroyAllWindows()