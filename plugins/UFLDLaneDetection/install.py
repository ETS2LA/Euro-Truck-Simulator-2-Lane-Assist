requirements = ["numpy", "opencv-python", "onnxruntime", "onnx"]
import os


# This function will be run when the plugin is first discovered.
# It is recommended to download all requirements here!
def install():
    
    for requirement in requirements:
        os.system("pip install " + requirement)
        
    pass