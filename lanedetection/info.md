Each model folder should have it's own files, as well as a model.py file.
You should check the lstr folder for an example!

This file should have the following functions : 

1. ```str[] discover_models()```
Will return all downloaded models in /lanedetection/'modelname'/models.

2. ```bool load_model(name, useGPU)```
Will do everything necessary to load the model of said name and return true or false depending on success.

3. ```image,int compute_lanes(image, steering_offset, draw_points=True, draw_poly=True, color=(255,191,0))```
Should return an image of the detected lanes, as well as the computed difference.