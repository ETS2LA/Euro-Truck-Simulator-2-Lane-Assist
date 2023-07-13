requirements = ["numpy", "opencv-python", "onnxruntime", "onnx", "onnxruntime-gpu"]
secondRequirements = ["pycuda"]
import os


# This function will be run when the plugin is first discovered.
# It is recommended to download all requirements here!
def install():
    
    for requirement in requirements:
        os.system("pip install " + requirement)
        
    for requirement in secondRequirements:
        os.system("pip install " + requirement)
        
    pass