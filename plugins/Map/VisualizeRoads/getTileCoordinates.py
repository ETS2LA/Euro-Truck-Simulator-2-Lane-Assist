"""
Download the map from 
https://github.com/Unicor-p/ts-map#map-available

Place the levels from there to 
/Tiles

Example
/Tiles/1
/Tiles/2
/Tiles/3
etc...

Then run this script.

Each pixel at lvl8 = one meter in game
This means we can easily get the coordinates of the lanes from the map, as long as we can detect them.

Only problem is it would still be +- 1 meter, so we have to do some pretty heavy interpolation
to get usable coordinates on the app side.

"""


import os
from os import listdir
from os.path import isdir, join
import json
import time

# Tile settings
maxX = 131072
maxY = 131072
tileSize = 512
maxZoom = 8

# File settings
tilePath = "Tiles/8/"
folderAxis = "X"
fileAxis = "Y"

data = {
    "folders": {},
}

for folder in range(0, int(maxY/tileSize)):
    data["folders"][folder] = {}
    data["folders"][folder]["files"] = {}
    for file in range(0, int(maxY/tileSize)):
        data["folders"][folder]["files"][file] = {}
        data["folders"][folder]["files"][file]["x"] = int(folder) * tileSize
        data["folders"][folder]["files"][file]["y"] = int(file) * tileSize
        
def ConvertGameXYToPixelXY(x,y):
    # https://github.com/dariowouters/ts-map/issues/16#issuecomment-716160718
    
    xy = [x,y]
    # Values from TileMapInfo.json
    x1 = -94505.8047
    x2 = 79254.13
    y1 = -80093.17
    y2 = 93666.7656
    
    xtot = x2 - x1; # Total X length
    ytot = y2 - y1; # Total Y length

    xrel = (xy[0] - x1) / xtot; # The fraction where the X is (between 0 and 1, 0 being fully left, 1 being fully right)
    yrel = (xy[1] - y1) / ytot; # The fraction where the Y is

    return [
        xrel * maxX, # Where X actually is, so multiplied the actual width
        maxY - (yrel * maxY) # Where Y actually is, only Y is inverted
    ]
    
def ConvertPixelXYToGameXY(x,y):
    # Derived from https://github.com/dariowouters/ts-map/issues/16#issuecomment-716160718
    xy = [x,y]
    # Values from TileMapInfo.json
    x1 = -94505.8047
    x2 = 79254.13
    y1 = -80093.17
    y2 = 93666.7656
    
    xtot = x2 - x1; # Total X length
    ytot = y2 - y1; # Total Y length
    
    xrel = xy[0] / maxX
    yrel = xy[1] / maxY
    
    x = x1 + (xrel * xtot)
    y = y1 + (yrel * ytot)
    
    return [x,y]
    

if __name__ == "__main__":
    # Make an image 10th of the size of the map
    # And populate that with the tiles
    # Then save that image as a png
    from PIL import Image
    import cv2
    import numpy as np

    # Recommended > 10
    sizeDivider = 10
    laneColor = [255, 220, 80]
    map = Image.new("RGB", (int(maxX/sizeDivider), int(maxY/sizeDivider)), (0, 0, 0))
    mapNoEdits = Image.new("RGB", (int(maxX/sizeDivider), int(maxY/sizeDivider)), (0, 0, 0))

    range = 30

    for folder in data["folders"]:
        startTime = time.time()
        for file in data["folders"][folder]["files"]:
            tile = Image.open(tilePath + str(folder) + "/" + str(file) + ".png")
            
            mapNoEdits.paste(tile, (int(folder * tileSize/sizeDivider), int(file * tileSize/sizeDivider)))
            
            tile = tile.resize((int(tileSize/sizeDivider), int(tileSize/sizeDivider)))
            
            # Remove everything not within 10 pixels of the lane color
            tile = cv2.cvtColor(np.array(tile), cv2.COLOR_RGB2BGR)
            tile = cv2.inRange(tile, np.array([laneColor[2]-range, laneColor[1]-range, laneColor[0]-range]), np.array([laneColor[2]+range, laneColor[1]+range, laneColor[0]+range]))
            
            
            tile = Image.fromarray(tile)
            
            map.paste(tile, (int(folder * tileSize/sizeDivider), int(file * tileSize/sizeDivider)))
        
        timeFor = time.time() - startTime
        print(f"{folder} | {round(folder/255 * 100)}% | {round(timeFor * (255-folder/255))}s ", end="\r")
            
    print("Saving map.png")
    map.save("map.png")