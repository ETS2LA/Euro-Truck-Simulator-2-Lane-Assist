# This file is in charge of loading plugins, as well as the main loop of the program.
import os
import sys
import time
import json

LANE_DETECTION_PATH = os.path.join(os.path.dirname(__file__), "lanedetection")

'''

This part will discover all possible lane detection models.
It will then prompt the user into selecting one. This will in the future happen in the UI.

'''
print("Discovering lane detection models...")
# Find all models in the models folder
folders = []
for file in os.listdir(LANE_DETECTION_PATH):
    folders.append(file)

# Check for model.py
models = []
for folder in folders:
    if os.path.exists(os.path.join(LANE_DETECTION_PATH, folder, "model.py")):
        models.append(folder)

# Select model
print("Type the number of the model you wish to use:")
for i in range(len(models)):
    print(str(i) + ": " + models[i])
number = input("> ")

# Load model
model = models[int(number)]
print("Loading model: " + model)
laneDetection = __import__("lanedetection." + model + ".model", fromlist=["model"])
print("Loaded model")

# Select previous model checkpoint
checkpoints = laneDetection.discover_models()
print("Type the number of the checkpoint you wish to use:")
for i in range(len(checkpoints)):
    print(str(i) + ": " + checkpoints[i])
number = input("> ")

