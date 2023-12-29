import onnxruntime
import cv2
import time, os
import numpy as np
try :
	from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.utils import LaneModelType, OffsetType, lane_colors, tusimple_row_anchor, culane_row_anchor
except :
	from .utils import LaneModelType, OffsetType, lane_colors, tusimple_row_anchor, culane_row_anchor

# This will temporarily add the NVIDIA CUDA libraries to the system path
import os
import src.variables as variables

nvidiaPath = "src/NVIDIA"
nvidiaPath = os.path.join(variables.PATH, nvidiaPath)

os.environ["PATH"] = nvidiaPath

def _softmax(x) :
	exp_x = np.exp(x)
	return exp_x/np.sum(exp_x)

class ModelConfig():

	def __init__(self, model_type):

		if model_type == LaneModelType.UFLDV2_TUSIMPLE:
			self.init_tusimple_config()
		else:
			self.init_culane_config()
		self.num_lanes = 4

	def init_tusimple_config(self):
		self.img_w = 800
		self.img_h = 320
		self.row_anchor = tusimple_row_anchor
		self.griding_num = 100
		self.crop_ratio = 0.8
		self.row_anchor = np.linspace(160,710, 56)/720
		self.col_anchor = np.linspace(0,1, 41)

	def init_culane_config(self):
		self.img_w = 1600
		self.img_h = 320
		self.row_anchor = culane_row_anchor
		self.griding_num = 200
		self.crop_ratio = 0.6
		self.row_anchor = np.linspace(0.42,1, 72)
		self.col_anchor = np.linspace(0,1, 81)

class OnnxEngine():

	def __init__(self, onnx_file_path, useGPU=True):
		if (onnxruntime.get_device() == 'GPU' and useGPU) :
			self.session = onnxruntime.InferenceSession(onnx_file_path, providers=['CUDAExecutionProvider'])
			print("ONNX Running with GPU support.")
		else :
			self.session = onnxruntime.InferenceSession(onnx_file_path, providers=['CPUExecutionProvider'])
			print("ONNX Running with CPU support.")
		self.providers = self.session.get_providers()

	def  get_onnx_input_shape(self):
		return self.session.get_inputs()[0].shape


	def  get_onnx_output_shape(self):
		output_shape = [output.shape for output in self.session.get_outputs()]
		output_names = [output.name for output in self.session.get_outputs()]
		if (len(output_names) != 4) :
			raise Exception("Output dims is error, please check model. load %d channels not match 4." % len(self.output_names))
		return output_shape, output_names
	
	def inference(self, input_tensor):
		input_name = self.session.get_inputs()[0].name
		output_names = [output.name for output in self.session.get_outputs()]
		output = self.session.run(output_names, {input_name: input_tensor})

		return output

class UltrafastLaneDetectorV2():
	_defaults = {
		"model_path": "models/culane_res18.onnx",
		"model_type" : LaneModelType.UFLDV2_TUSIMPLE,
	}

	@classmethod
	def set_defaults(cls, config) :
		cls._defaults = config

	@classmethod
	def check_defaults(cls):
		return cls._defaults
		
	@classmethod
	def get_defaults(cls, n):
		if n in cls._defaults:
			return cls._defaults[n]
		else:
			return "Unrecognized attribute name '" + n + "'"

	def __init__(self, model_path=None, model_type=None, logger=None):
		if (None in [model_path, model_type]) :
			self.__dict__.update(self._defaults) # set up default values
		else :
			self.model_path = model_path
			self.model_type = model_type
		self.logger = logger

		if ( self.model_type not in [LaneModelType.UFLDV2_TUSIMPLE, LaneModelType.UFLDV2_CULANE]) :
			if (self.logger) :
				self.logger.error("UltrafastLaneDetectorV2 can use %s type." % self.model_type.name)
			raise Exception("UltrafastLaneDetectorV2 can use %s type." % self.model_type.name)

		self.fps = 0
		self.timeLastPrediction = time.time()
		self.frameCounter = 0
		self.draw_area_points = []
		self.draw_area = False

		# Load model configuration based on the model type
		self.cfg = ModelConfig(self.model_type)

		# Initialize model
		self._initialize_model(self.model_path, self.cfg)
		
	def _initialize_model(self, model_path, cfg):
		if (self.logger) :
			self.logger.debug("model path: %s." % model_path)
		if not os.path.isfile(model_path):
			raise Exception("The model path [%s] can't not found!" % model_path)

		self.framework_type = "onnx"
		self.infer = OnnxEngine(model_path)
		self.providers = self.infer.providers

		# Get model info
		self.getModel_input_details()
		self.getModel_output_details()
		if (self.logger) :
			self.logger.info(f'UfldDetector Type : [{self.framework_type}] || Version : [{self.providers}]')

	def getModel_input_details(self):
		if (self.framework_type == "trt") :
			self.input_shape = self.infer.get_tensorrt_input_shape()
		else :
			self.input_shape = self.infer.get_onnx_input_shape()
		self.channes = self.input_shape[1]
		self.input_height = self.input_shape[2]
		self.input_width = self.input_shape[3]

	def getModel_output_details(self):
		if (self.framework_type == "trt") :
			self.output_shape = self.infer.get_tensorrt_output_shape()
		else :
			self.output_shape, self.output_names = self.infer.get_onnx_output_shape()

	def prepare_input(self, image):
		img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		self.img_height, self.img_width, self.img_channels = img.shape


		# Input values should be from -1 to 1 with a size of 288 x 800 pixels
		new_size = ( self.input_width, int(self.input_height/self.cfg.crop_ratio))
		img_input = cv2.resize(img, new_size).astype(np.float32)
		img_input = img_input[-self.input_height:, :, :]
		# Scale input pixel values to -1 to 1
		mean=[0.485, 0.456, 0.406]
		std=[0.229, 0.224, 0.225]
		
		img_input = ((img_input/ 255.0 - mean) / std)
		img_input = img_input.transpose(2, 0, 1)
		img_input = img_input[np.newaxis,:,:,:]        

		return img_input.astype(np.float32)

	def DetectFrame(self, image) :
		input_tensor = self.prepare_input(image)

		# Perform inference on the image
		output = self.infer.inference(input_tensor)

		# Process output data
		self.lanes_points, self.lanes_detected = self.process_output(output, self.cfg, original_image_width =  self.img_width, original_image_height = self.img_height)

	def DrawDetectedOnFrame(self, image, type=OffsetType.UNKNOWN) :
		for lane_num,lane_points in enumerate(self.lanes_points):
			if ( lane_num==1 and type == OffsetType.RIGHT) :
				color = (0, 0, 255)
			elif (lane_num==2 and type == OffsetType.LEFT) :
				color = (0, 0, 255)
			else :
				color = lane_colors[lane_num]
			for lane_point in lane_points:
				cv2.circle(image, (lane_point[0],lane_point[1]), 3, color, -1)

	def DrawAreaOnFrame(self, image, color=(255,191,0)) :
		self.draw_area = False
		# Draw a mask for the current lane
		if(self.lanes_detected != []) :
			if(self.lanes_detected[1] and self.lanes_detected[2]):
				self.draw_area = True
				lane_segment_img = image.copy()
				left_lanes_points, right_lanes_points = self.adjust_lanes_points(self.lanes_points[1], self.lanes_points[2], self.img_height)
				self.draw_area_points = [np.vstack((left_lanes_points,np.flipud(right_lanes_points)))]
				cv2.fillPoly(lane_segment_img, pts = self.draw_area_points, color =color)
				image = cv2.addWeighted(image, 0.7, lane_segment_img, 0.1, 0)

		if (not self.draw_area) : self.draw_area_points = []
		return image

	def AutoDrawLanes(self, image, draw_points=True):

		input_tensor = self.prepare_input(image)

		# Perform inference on the image
		output = self.infer.inference(input_tensor)

		# Process output data
		try:
			self.lanes_points, self.lanes_detected = self.process_output(output, self.cfg, original_image_width =  self.img_width, original_image_height = self.img_height)
		except:
			import traceback
			traceback.print_exc()

		# # Draw depth image
		visualization_img = self.draw_lanes(image, self.lanes_points, self.lanes_detected, draw_points, original_image_width =  self.img_width, original_image_height = self.img_height)

		return visualization_img

	def adjust_lanes_points(self, left_lanes_points, right_lanes_points, image_height) : 
		# 多项式拟合
		if (len(left_lanes_points[1]) != 0 ) :
			leftx, lefty  = list(zip(*left_lanes_points))
		else :
			return left_lanes_points, right_lanes_points
		if (len(right_lanes_points) != 0 ) :
			rightx, righty  = list(zip(*right_lanes_points))
		else :
			return left_lanes_points, right_lanes_points

		if len(lefty) > 10:
			self.left_fit = np.polyfit(lefty, leftx, 2)
		if len(righty) > 10:
			self.right_fit = np.polyfit(righty, rightx, 2)

		# Generate x and y values for plotting
		maxy = image_height - 1
		miny = image_height // 3
		if len(lefty):
			maxy = max(maxy, np.max(lefty))
			miny = min(miny, np.min(lefty))

		if len(righty):
			maxy = max(maxy, np.max(righty))
			miny = min(miny, np.min(righty))

		ploty = np.linspace(miny, maxy, image_height)

		left_fitx = self.left_fit[0]*ploty**2 + self.left_fit[1]*ploty + self.left_fit[2]
		right_fitx = self.right_fit[0]*ploty**2 + self.right_fit[1]*ploty + self.right_fit[2]

		# Visualization
		fix_left_lanes_points = []
		fix_right_lanes_points = []
		for i, y in enumerate(ploty):
			l = int(left_fitx[i])
			r = int(right_fitx[i])
			y = int(y)
			if (y >= min(lefty)) :
				fix_left_lanes_points.append((l, y))
			if (y >= min(righty)) :
				fix_right_lanes_points.append((r, y))
				# cv2.line(out_img, (l, y), (r, y), (0, 255, 0))
		return fix_left_lanes_points, fix_right_lanes_points

	@staticmethod
	def process_output(pred, cfg, local_width = 1, original_image_width = 1640, original_image_height = 590):

		output = {"loc_row" : pred[0], 'loc_col' : pred[1], "exist_row" : pred[2], "exist_col" : pred[3]}
		# print(output["loc_row"].shape)
		# print(output["exist_row"].shape)
		# print(output["loc_col"].shape)
		# print(output["exist_col"].shape)

		batch_size, num_grid_row, num_cls_row, num_lane_row = output['loc_row'].shape
		batch_size, num_grid_col, num_cls_col, num_lane_col = output['loc_col'].shape

		max_indices_row = output['loc_row'].argmax(1)
		# n , num_cls, num_lanes
		valid_row = output['exist_row'].argmax(1)
		# n, num_cls, num_lanes

		max_indices_col = output['loc_col'].argmax(1)
		# n , num_cls, num_lanes
		valid_col = output['exist_col'].argmax(1)
		# n, num_cls, num_lanes

		output['loc_row'] = output['loc_row']
		output['loc_col'] = output['loc_col']
		row_lane_idx = [1,2]
		col_lane_idx = [0,3]

		# Parse the output of the model
		lanes_points = {"left-side" : [], "left-ego" : [] , "right-ego" : [], "right-side" : []}
		# lanes_detected = []
		lanes_detected =  {"left-side" : False, "left-ego" : False , "right-ego" : False, "right-side" : False}
		for i in row_lane_idx:
			tmp = []
			if valid_row[0,:,i].sum() > num_cls_row / 2:
				for k in range(valid_row.shape[1]):
					if valid_row[0,k,i]:
						all_ind = list(range(max(0,max_indices_row[0,k,i] - local_width), min(num_grid_row-1, max_indices_row[0,k,i] + local_width) + 1))
						out_tmp = ( _softmax(output['loc_row'][0,all_ind,k,i]) * list(map(float, all_ind))).sum() + 0.5
						out_tmp = out_tmp / (num_grid_row-1) * original_image_width
						tmp.append((int(out_tmp), int(cfg.row_anchor[k] * original_image_height)))
				if (i == 1) :
					lanes_points["left-ego"].extend(tmp)
					if (len(tmp) > 2) :
						lanes_detected["left-ego"] = True
				else :
					lanes_points["right-ego"].extend(tmp)
					if (len(tmp) > 2) :
						lanes_detected["right-ego"] = True

		for i in col_lane_idx:
			tmp = []
			if valid_col[0,:,i].sum() > num_cls_col / 4:
				for k in range(valid_col.shape[1]):
					if valid_col[0,k,i]:
						all_ind = list(range(max(0,max_indices_col[0,k,i] - local_width), min(num_grid_col-1, max_indices_col[0,k,i] + local_width) + 1))
						out_tmp = ( _softmax(output['loc_col'][0,all_ind,k,i]) * list(map(float, all_ind))).sum() + 0.5
						out_tmp = out_tmp / (num_grid_col-1) * original_image_height
						tmp.append((int(cfg.col_anchor[k] * original_image_width), int(out_tmp)))
				if (i == 0) :
					lanes_points["left-side" ].extend(tmp)
					if (len(tmp) > 2) :
						lanes_detected["left-side"] = True
				else :
					lanes_points["right-side"].extend(tmp)
					if (len(tmp) > 2) :
						lanes_detected["right-side"] = True

		#print(lanes_detected)
		return list(lanes_points.values()), list(lanes_detected.values())

	@staticmethod
	def draw_lanes(input_img, lanes_points, lanes_detected, cfg, draw_points=True, original_image_width = 1640, original_image_height = 590):
		# Write the detected line points in the image
		visualization_img = cv2.resize(input_img, (original_image_width, original_image_height), interpolation = cv2.INTER_AREA)

		# Draw a mask for the current lane
		if(lanes_detected != []) :
			if(lanes_detected[1] and lanes_detected[2]):
				lane_segment_img = visualization_img.copy()
				
				cv2.fillPoly(lane_segment_img, pts = [np.vstack((lanes_points[1],np.flipud(lanes_points[2])))], color =(255,191,0))
				visualization_img = cv2.addWeighted(visualization_img, 0.7, lane_segment_img, 0.3, 0)

		if(draw_points):
			for lane_num,lane_points in enumerate(lanes_points):
				for lane_point in lane_points:
					cv2.circle(visualization_img, (lane_point[0],lane_point[1]), 3, lane_colors[lane_num], -1)

		return visualization_img