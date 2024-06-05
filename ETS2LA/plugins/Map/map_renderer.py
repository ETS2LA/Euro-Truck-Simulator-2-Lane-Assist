import numpy as np
import keyboard
import json
import cv2
import os
import time

PATH = os.path.dirname(os.path.abspath(__file__))
if "Map" not in PATH:
    PATH += "\\ETS2LA\\plugins\\Map\\"
if not PATH.endswith("\\"):
    PATH += "\\"

def getFilePath(x, y):
    return PATH + "Images\\%d_%d.png" % (x, y)

# Get the JSON data
with open(PATH + 'Images\\data.json') as f:
    data = json.load(f)
    
xWidth = int(data["widthTiles"])
yWidth = int(data["heightTiles"])
tileResolution = int(data["meterResolution"])

images = [[None for y in range(yWidth)] for x in range(xWidth)]

def getTile(x, y):
    if images[x][y] is None:
        images[x][y] = cv2.imread(getFilePath(x, y))
        
    return images[x][y]

startX = xWidth * tileResolution / 2
startY = yWidth * tileResolution / 2

def convertFromPixelToMeter(x, y):
    return (x - startX) / tileResolution, (startY - y) / tileResolution

def convertFromMeterToPixel(x, y):
    return int(startX + x * tileResolution), int(startY - y * tileResolution)

X = startX
Y = startY
ZOOM = 1

# Define the callback function
dragging = False
startX, startY = -1, -1

def drag(event, x, y, flags, param):
    global X, Y, dragging, startX, startY, ZOOM
    if event == cv2.EVENT_LBUTTONDOWN:
        dragging = True
        startX, startY = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if dragging:
            X -= (x - startX) / ZOOM
            Y -= (y - startY) / ZOOM
            startX, startY = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False
    elif event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:  # scroll up
            ZOOM *= 1.1
            if ZOOM > 1:
                ZOOM = 1
        else:  # scroll down
            ZOOM /= 1.1

# Set the callback function for the window
cv2.namedWindow('Map')
cv2.setMouseCallback('Map', drag)

while True:
    startTime = time.time()
    # Interpolate the nearest 3x3 tiles
    xTile = int(X / tileResolution)
    yTile = int(Y / tileResolution)
    
    if xTile < 0 or xTile >= xWidth or yTile < 0 or yTile >= yWidth:
        print(f"Out of bounds ({xTile}, {yTile})")
        continue
    
    xTilePos = xTile * tileResolution
    yTilePos = yTile * tileResolution
    
    try:
        # Get the tiles
        tiles = []
        tileCount = int(1 / ZOOM)  # Adjust this as needed
        for i in range(-tileCount, tileCount + 1):
            for j in range(-tileCount, tileCount + 1):
                tiles.append((i, j, getTile(xTile + i, yTile + j)))
        
        # Draw the images with the correct offset
        baseImage = np.zeros((tileResolution * 3, tileResolution * 3, 3), np.uint8)
        
        # Move the images so that the x, y is in the center
        for dx, dy, tile in tiles:
            if tile is not None:
                x_offset = int((dx + 1) * tileResolution * ZOOM)
                y_offset = int((dy + 1) * tileResolution * ZOOM)
                if 0 <= y_offset < baseImage.shape[0] and 0 <= x_offset < baseImage.shape[1]:
                    resizedTile = cv2.resize(tile, None, fx=ZOOM, fy=ZOOM, interpolation=cv2.INTER_LINEAR)
                    baseImage[y_offset:y_offset+resizedTile.shape[0], x_offset:x_offset+resizedTile.shape[1]] = resizedTile
        
        # Crop the baseImage to keep the center around the x, y
        x_offset = int(int(X - xTilePos) * ZOOM)
        y_offset = int(int(Y - yTilePos) * ZOOM)
        baseImage = baseImage[y_offset:y_offset+tileResolution, x_offset:x_offset+tileResolution]
        
        # Draw the position on the map
        endTime = time.time()
        cv2.putText(baseImage, f"({X}, {Y})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(baseImage, f"FPS: {round(1 / (endTime - startTime))}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow('Map', baseImage)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        import traceback
        traceback.print_exc()

