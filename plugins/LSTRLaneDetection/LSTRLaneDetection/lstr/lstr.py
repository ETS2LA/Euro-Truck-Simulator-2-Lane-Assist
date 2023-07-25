import sys
import os
import cv2
import time
import numpy as np
import onnx
import onnxruntime
import shutil
import src.variables as variables

# This will temporarily add the NVIDIA CUDA libraries to the system path

nvidiaPath = "src/NVIDIA"
nvidiaPath = os.path.join(variables.PATH, nvidiaPath)

os.environ["PATH"] = nvidiaPath


# from google_drive_downloader import GoogleDriveDownloader as gdd

lane_colors = [(68,65,249),(44,114,243),(30,150,248),(74,132,249),(79,199,249),(109,190,144),(142, 144, 77),(161, 125, 39)]
log_space = np.logspace(0,2, 50, base=1/10, endpoint=True)

class LSTR():

    def __init__(self, model_type, model_path, use_gpu=True):

        # Initialize model (download if necessary)
        # models_gdrive_id = "1uSyVLlZn0NDoa7RR3U6vG_OCkn0uoE8z"
        # download_gdrive_tar_model(models_gdrive_id, model_type, model_path)
        self.model = self.initialize_model(model_path, use_gpu=use_gpu)

    def __call__(self, image):

        return self.detect_lanes(image)

    def initialize_model(self, model_path, use_gpu=True):

        if use_gpu:
            try:
                self.session = onnxruntime.InferenceSession(model_path, providers=['CUDAExecutionProvider', 'TensorrtExecutionProvider'])
                print("ONNX Runtime with CUDA support found, using GPU")
            except:
                self.session = onnxruntime.InferenceSession(model_path, providers=['CUDAExecutionProvider'])
                print("ONNX Runtime with CUDA support not found, using CPU instead")
        else:
            self.session = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])

        # Get model info
        self.getModel_input_details()
        self.getModel_output_details()

    def detect_lanes(self, image):

        input_tensor, mask_tensor = self.prepare_inputs(image)
        
        outputs = self.inference(input_tensor, mask_tensor)

        detected_lanes, good_lanes = self.process_output(outputs)

        return detected_lanes, good_lanes

    def prepare_inputs(self, img):

        self.img_height, self.img_width, self.img_channels = img.shape

        # Transform the image for inference
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img,(self.input_width, self.input_height))


        # Scale input pixel values to -1 to 1
        mean=[0.485, 0.456, 0.406]
        std=[0.229, 0.224, 0.225]
        

        img = ((img/ 255.0 - mean) / std)
        # img = img/ 255.0

        img = img.transpose(2, 0, 1)
        input_tensor = img[np.newaxis,:,:,:].astype(np.float32)

        mask_tensor = np.zeros((1, 1, self.input_height, self.input_width), dtype=np.float32)
        

        return input_tensor, mask_tensor

    def inference(self, input_tensor, mask_tensor):

        outputs = self.session.run(self.output_names, {self.rgb_input_name: input_tensor, 
                                                       self.mask_input_name: mask_tensor})

        return outputs

    @staticmethod
    def softmax(x):
        """Compute softmax values for each sets of scores in x."""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=-1).T

    def process_output(self, outputs):  

        pred_logits = outputs[0]
        pred_curves = outputs[1]

        # Filter good lanes based on the probability
        prob = self.softmax(pred_logits)
        good_detections = np.where(np.argmax(prob,axis=-1)==1)
        pred_logits = pred_logits[good_detections]
        pred_curves = pred_curves[good_detections]

        lanes = []
        for lane_data in pred_curves:
            bounds = lane_data[:2]
            k_2, f_2, m_2, n_1, b_2, b_3 = lane_data[2:]

            # Calculate the points for the lane
            # Note: the logspace is used for a visual effect, np.linspace would also work as in the original repository
            y_norm = bounds[0]+log_space*(bounds[1]-bounds[0])
            x_norm = (k_2 / (y_norm - f_2) ** 2 + m_2 / (y_norm - f_2) + n_1 + b_2 * y_norm - b_3)
            lane_points = np.vstack((x_norm*self.img_width, y_norm*self.img_height)).astype(int)
            
            lanes.append(lane_points)    

        self.lanes = lanes
        self.good_lanes = good_detections[1]

        return lanes, self.good_lanes

    def getModel_input_details(self):

        model_inputs = self.session.get_inputs()
        self.rgb_input_name = self.session.get_inputs()[0].name
        self.mask_input_name = self.session.get_inputs()[1].name

        self.input_shape = self.session.get_inputs()[0].shape
        self.input_height = self.input_shape[2]
        self.input_width = self.input_shape[3]

    def getModel_output_details(self):

        model_outputs = self.session.get_outputs()
        self.output_names = [model_outputs[i].name for i in range(len(model_outputs))]
        # print(self.output_names)

    def draw_lanes(self,input_img, color=(255,191,0), fillPoly=False):

        # Write the detected line points in the image
        visualization_img = input_img.copy()

        # Draw a mask for the current lane
        right_lane = np.where(self.good_lanes==0)[0]
        left_lane = np.where(self.good_lanes==5)[0]

        if(len(left_lane) and len(right_lane)):
            
            lane_segment_img = visualization_img.copy()

            points = np.vstack((self.lanes[left_lane[0]].T,
                                np.flipud(self.lanes[right_lane[0]].T)))
            if fillPoly: cv2.fillConvexPoly(lane_segment_img, points, color=color)
            visualization_img = cv2.addWeighted(visualization_img, 0.7, lane_segment_img, 0.3, 0)
            
        for lane_num,lane_points in zip(self.good_lanes, self.lanes):
            for lane_point in lane_points.T:
                cv2.circle(visualization_img, (lane_point[0],lane_point[1]), 3, lane_colors[lane_num], -1)

        return visualization_img

# def download_gdrive_tar_model(gdrive_id, model_type, model_path):
# 
#     model_name = model_type.value
# 
#     if not os.path.exists(model_path):
#         gdd.download_file_from_google_drive(file_id=gdrive_id,
#                                     dest_path='./tmp/tmp.tar.gz')
#         tar = tarfile.open("tmp/tmp.tar.gz", "r:gz")
#         tar.extractall(path="tmp/")
#         tar.close()
# 
#         shutil.move(f"tmp/{model_name}/{model_name}.onnx", model_path)
#         shutil.rmtree("tmp/")

# def download_gdrive_file_model(model_path, gdrive_id):
#     if not os.path.exists(model_path):
#         gdd.download_file_from_google_drive(file_id=gdrive_id,
#                                     dest_path=model_path)

if __name__ == '__main__':

    from enum import Enum
    from imread_from_url import imread_from_url

    class ModelType(Enum):
        LSTR_180X320 = "lstr_180x320"
        LSTR_240X320 = "lstr_240x320"
        LSTR_360X640 = "lstr_360x640"
        LSTR_480X640 = "lstr_480x640"
        LSTR_720X1280 = "lstr_720x1280"

    model_type = ModelType.LSTR_360X640
    model_path = f"../models/{model_type.value}.onnx"

    lane_detector = LSTR(model_type, model_path)

    img = imread_from_url("https://live.staticflickr.com/1067/1475776461_f9adc2fee9_o_d.jpg")
    detected_lanes, lane_ids = lane_detector(img)

    lane_img = lane_detector.draw_lanes(img)
    cv2.namedWindow("Detected lanes", cv2.WINDOW_NORMAL)
    cv2.imshow("Detected lanes",lane_img)
    cv2.waitKey(0)

