'''
This file will discover and store an array of all possible models.
'''

from src.variables import PATH
import os

LANE_DETECTION_PATH = os.path.join(PATH, "lanedetection")

models = []

def FindModels():
    global models

    # Find all models in the models folder
    folders = []
    for file in os.listdir(LANE_DETECTION_PATH):
        folders.append(file)

    # Check for model.py
    models = []
    for folder in folders:
        if os.path.exists(os.path.join(LANE_DETECTION_PATH, folder, "model.py")):
            models.append(folder)

FindModels()