requirements = ["numpy", "opencv-python", "pycuda", "onnxruntime", "onnx"]
import os


# This fucntion will be run when the plugin is first discovered.
# It is recommended to download all requirements here!
def install():
    
    for requirement in requirements:
        os.system("pip install " + requirement)
        
    pass