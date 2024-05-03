from transformers import AutoModelForDepthEstimation, AutoImageProcessor
from PIL import Image
import requests
from ETS2LA.plugins.runner import PluginRunner  
import cv2
import numpy as np
import time
import torch

# load image
url = 'https://media.discordapp.net/attachments/1120721175337775124/1235728372395675730/3.png?ex=663615fa&is=6634c47a&hm=df2c1192545f9dddd12952888934879ec2f99d3319b69cea71b1b472c0f29248&=&format=webp&quality=lossless&width=885&height=498'
image = Image.open(requests.get(url, stream=True).raw)
runner:PluginRunner = None
RESOLUTION_SCALE = 1/4

def Initialize():
    global SI
    global SC
    global image_processor
    global model
    global device
    SI = runner.modules.ShowImage
    SC = runner.modules.ScreenCapture
    SC.monitor_x1 = 2150
    SC.monitor_y1 = 350
    SC.monitor_x2 = SC.monitor_x1 + 1500
    SC.monitor_y2 = SC.monitor_y1 + 600
    # load pipe
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using {device}")
    image_processor = AutoImageProcessor.from_pretrained("LiheYoung/depth-anything-small-hf", device=device)
    model = AutoModelForDepthEstimation.from_pretrained("LiheYoung/depth-anything-small-hf").to(device)

def plugin():
    startTime = time.time()
    cropped, image = SC.run()
    # Lower the resolution to a 1/4
    cropped = cv2.resize(cropped, (0,0), fx=RESOLUTION_SCALE, fy=RESOLUTION_SCALE)
    # prepare image for the model
    inputs = image_processor(images=cropped, return_tensors="pt", do_resize=False, do_normalize=False)
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}
    # predict depth
    with torch.no_grad():
        outputs = model(**inputs)
        predicted_depth = outputs.predicted_depth
    # interpolate to original size
    prediction = torch.nn.functional.interpolate(
        predicted_depth.unsqueeze(1),
        size=cropped.shape[:2],
        mode="bicubic",
        align_corners=False,
    )
    # visualize
    output = prediction.squeeze().cpu().numpy()
    formatted = (output * 255 / np.max(output)).astype("uint8")
    depth = cv2.applyColorMap(formatted, cv2.COLORMAP_BONE)
    endTime = time.time()
    # Add text
    cv2.putText(depth, f"FPS: {round(1/(endTime-startTime), 2)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    SI.run(depth)