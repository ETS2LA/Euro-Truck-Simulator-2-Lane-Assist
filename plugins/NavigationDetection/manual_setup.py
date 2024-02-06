from tkinter import messagebox
import numpy as np
import pyautogui
import ctypes
import mouse
import math
import json
import time
import cv2
import os

screenshot = pyautogui.screenshot()
setupframe = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
frame_width = setupframe.shape[1]
frame_height = setupframe.shape[0]

current_text = f"Loading..."
width_target_current_text = 0.5*frame_width
fontscale_current_text = 1
textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
width_current_text, height_current_text = textsize_current_text
max_count_current_text = 3
while width_current_text != width_target_current_text:
    fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text -= 1
    if max_count_current_text <= 0:
        break
thickness_current_text = round(fontscale_current_text*2)
if thickness_current_text <= 0:
    thickness_current_text = 1
cv2.namedWindow('Setup', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Setup', round(frame_width/2), round(frame_height/2))
startframe = np.zeros((round(frame_height), round(frame_width), 3))
cv2.putText(startframe, "Loading...", (round(frame_width/2-width_current_text/2), round(frame_height/2+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA) 

file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
exampleimage = cv2.imread(file_path + r"\assets\NavigationDetection\setupexample.png")
currentProfile = os.path.join(file_path, "profiles", "currentProfile.txt")

cv2.namedWindow('Example Image', cv2.WINDOW_NORMAL)
exampleimage_width = exampleimage.shape[1]
exampleimage_height = exampleimage.shape[0]
cv2.resizeWindow('Example Image', round(exampleimage_width/2), round(exampleimage_height/2))
cv2.imshow('Example Image', exampleimage)
cv2.imshow('Setup', startframe)
cv2.waitKey(1)

def EnsureFile(file:str):
    try:
        with open(file, "r") as f:
            pass
    except:
        with open(file, "w") as f:
            f.write("{}")

def GetSettings(category:str, name:str, value:any=None):
    try:
        settings_file = os.path.join(file_path, "profiles", "settings.json")
        EnsureFile(settings_file)
        with open(settings_file, "r") as f:
            settings = json.load(f)
        
        if settings.get(category, {}).get(name) is None:
            return value    
        
        return settings[category][name]
    except Exception as ex:
        if value is not None:
            CreateSettings(category, name, value)
            return value
        else:
            pass

def CreateSettings(category:str, name:str, data:any):
    try:
        settings_file = os.path.join(file_path, "profiles", "settings.json")
        EnsureFile(settings_file)
        with open(settings_file, "r") as f:
            settings = json.load(f)

        settings.setdefault(category, {})
        settings[category][name] = data
            
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=6)
    except Exception as ex:
        print(ex)

# here are the button positions
# background x1, background y1, background x2, background y2, textposition x, textposition y, textscale
button_zoom_in = 0.0, 0.0, 0.1, 0.05, 0.0, 0.04, 1
button_zoom_out = 0.0, 0.07, 0.1, 0.12, 0.0, 0.11, 1
button_new_screenshot = 0.0, 0.14, 0.1, 0.22, 0.0, 0.20, 1
button_reset = 0.0, 0.24, 0.1, 0.29, 0.007, 0.28, 1
button_finish = 0.9, 0.0, 1.0, 0.1, 0.918, 0.08, 1
button_get_map_top_left = 0.15, 0.0, 0.475, 0.1, 0.15, 0.06, 0.8
button_get_map_bottom_right = 0.525, 0.0, 0.85, 0.1, 0.525, 0.06, 0.8
button_get_arrow_top_left =0.15, 0.15, 0.475, 0.25, 0.15, 0.21, 0.8
button_get_arrow_bottom_right = 0.525, 0.15, 0.85, 0.25, 0.525, 0.21, 0.8
button_area = 0.30

map_topleft = GetSettings("NavigationDetection", "map_topleft", "unset")
map_bottomright = GetSettings("NavigationDetection", "map_bottomright", "unset")
arrow_topleft = GetSettings("NavigationDetection", "arrow_topleft", "unset")
arrow_bottomright = GetSettings("NavigationDetection", "arrow_bottomright", "unset")
if map_topleft == "unset":
    map_topleft = None
if map_bottomright == "unset":
    map_bottomright = None
if arrow_topleft == "unset":
    arrow_topleft = None
if arrow_bottomright == "unset":
    arrow_bottomright = None

minimapDistanceFromRight = 27
minimapDistanceFromBottom = 134
minimapWidth = 560
minimapHeight = 293
scale = frame_height/1440
if map_topleft == None:
    xCoord = frame_width - (minimapDistanceFromRight * scale + minimapWidth * scale)
    yCoord = frame_height - (minimapDistanceFromBottom * scale + minimapHeight * scale)
    map_topleft = (int(xCoord), int(yCoord))
    CreateSettings("NavigationDetection", "map_topleft", map_topleft)
if map_bottomright == None:
    xCoord = frame_width - (minimapDistanceFromRight * scale)
    yCoord = frame_height - (minimapDistanceFromBottom * scale)
    map_bottomright = (int(xCoord), int(yCoord))
    CreateSettings("NavigationDetection", "map_bottomright", map_bottomright)
if arrow_topleft == None:
    xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.57
    yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.575
    arrow_topleft = (int(xCoord), int(yCoord))
    CreateSettings("NavigationDetection", "arrow_topleft", arrow_topleft)
if arrow_bottomright == None:
    xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.43
    yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.39
    arrow_bottomright = (int(xCoord), int(yCoord))
    CreateSettings("NavigationDetection", "arrow_bottomright", arrow_bottomright)

zoom = 0
zoomoffsetx = 0
zoomoffsety = 0
last_left_clicked = False
get_map_topleft = False
get_map_bottomright = False
get_arrow_topleft = False
get_arrow_bottomright = False

while True:
    frame = setupframe.copy()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]
    
    if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, 'Setup'):
        left_clicked = True
    else:
        left_clicked = False

    try:
        x1, y1, width, height = cv2.getWindowImageRect('Setup')
        x2, y2 = mouse.get_position()
        mousex = x2-x1
        mousey = y2-y1
        last_window_size = (x1, y1, width, height)
        last_mouse_position = (x2, y2)
    except:
        try:
            x1, y1, width, height = last_window_size
        except:
            x1, y1, width, height = (0, 0, 100, 100)
        try:
            x2, y2 = last_mouse_position
        except:
            x2, y2 = (0, 0)
        mousex = x2-x1
        mousey = y2-y1
        frame_width = setupframe.shape[1]
        frame_height = setupframe.shape[0]
        current_text = f"Loading..."
        width_target_current_text = 0.5*frame_width
        fontscale_current_text = 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text = 3
        while width_current_text != width_target_current_text:
            fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text -= 1
            if max_count_current_text <= 0:
                break
        thickness_current_text = round(fontscale_current_text*2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        cv2.namedWindow('Setup', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Setup', round(frame_width/2), round(frame_height/2))
        startframe = np.zeros((round(frame_height), round(frame_width), 3))
        cv2.putText(startframe, "Loading...", (round(frame_width/2-width_current_text/2), round(frame_height/2+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA) 
        cv2.imshow('Setup', startframe)
        cv2.waitKey(1)

    if width != 0 and height != 0:
        mouseposx = mousex/width
        mouseposy = mousey/height
    else:
        mouseposx = 0
        mouseposy = 0

    setupframetextsize = math.sqrt(width)/35
    setupframetextthickness = round(math.sqrt(width)/35)*2
    setupframelinethickness = round(math.sqrt(width)/35)*2
    if setupframetextthickness == 0:
        setupframetextthickness = 1
    if setupframelinethickness == 0:
        setupframelinethickness = 1

    corner1 = round(frame_height*zoom/100)+zoomoffsety
    corner2 = round(frame_height-frame_height*zoom/100)+zoomoffsety
    corner3 = round(frame_width*zoom/100)+zoomoffsetx
    corner4 = round(frame_width-frame_width*zoom/100)+zoomoffsetx

    if corner1 < 0:
        corner1 = 0
    if corner1 > frame_height:
        corner1 = frame_height

    if corner2 < 0:
        corner2 = 0
    if corner2 > frame_height:
        corner2 = frame_height

    if corner3 < 0:
        corner3 = 0
    if corner3 > frame_width:
        corner3 = frame_width

    if corner4 < 0:
        corner4 = 0
    if corner4 > frame_width:
        corner4 = frame_width

    original_pixel_x = round(corner3+mouseposx*(corner4-corner3))
    original_pixel_y = round(corner1+mouseposy*(corner2-corner1))

    if left_clicked == False:
        mousecoordroot = mouseposx, mouseposy
    if mousecoordroot == None:
        mousecoordroot = 0, 0

    if get_map_topleft == True:
        cv2.line(frame, (round(original_pixel_x), round(0*frame_height)), (round(original_pixel_x), round(1*frame_height)), (0,0,150), setupframelinethickness)
        cv2.line(frame, (round(0*frame_width), round(original_pixel_y)), (round(1*frame_width), round(original_pixel_y)), (0,0,150), setupframelinethickness)
        cv2.putText(frame, "Map Top Left", (round(original_pixel_x+setupframetextsize*5), round(original_pixel_y+setupframetextsize*30)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
        cv2.putText(frame, f"{round(original_pixel_x), round(original_pixel_y)}", (round(original_pixel_x+setupframetextsize*5), round(original_pixel_y-setupframetextsize*10)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
    else:
        if map_topleft != None:
            xpos, ypos = map_topleft
            cv2.line(frame, (round(xpos), round(0*frame_height)), (round(xpos), round(1*frame_height)), (0,0,150), setupframelinethickness)
            cv2.line(frame, (round(0*frame_width), round(ypos)), (round(1*frame_width), round(ypos)), (0,0,150), setupframelinethickness)
            cv2.putText(frame, "Map Top Left", (round(xpos+setupframetextsize*5), round(ypos+setupframetextsize*30)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
            cv2.putText(frame, f"({xpos}, {ypos})", (round(xpos+setupframetextsize*5), round(ypos-setupframetextsize*10)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)

    if get_map_bottomright == True:
        cv2.line(frame, (round(original_pixel_x), round(0*frame_height)), (round(original_pixel_x), round(1*frame_height)), (0,0,150), setupframelinethickness)
        cv2.line(frame, (round(0*frame_width), round(original_pixel_y)), (round(1*frame_width), round(original_pixel_y)), (0,0,150), setupframelinethickness)
        cv2.putText(frame, "Map Bottom Right", (round(original_pixel_x-setupframetextsize*290), round(original_pixel_y-setupframetextsize*10)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
        cv2.putText(frame, f"{round(original_pixel_x), round(original_pixel_y)}", (round(original_pixel_x-setupframetextsize*200), round(original_pixel_y+setupframetextsize*30)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
    else:
        if map_bottomright != None:
            xpos, ypos = map_bottomright
            cv2.line(frame, (round(xpos), round(0*frame_height)), (round(xpos), round(1*frame_height)), (0,0,150), setupframelinethickness)
            cv2.line(frame, (round(0*frame_width), round(ypos)), (round(1*frame_width), round(ypos)), (0,0,150), setupframelinethickness)
            cv2.putText(frame, "Map Bottom Right", (round(xpos-setupframetextsize*290), round(ypos-setupframetextsize*10)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)
            cv2.putText(frame, f"({xpos}, {ypos})", (round(xpos-setupframetextsize*200), round(ypos+setupframetextsize*30)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize, (0,0,150), setupframetextthickness, cv2.LINE_AA)

    if map_topleft != None and map_bottomright != None and get_map_topleft == False and get_map_bottomright == False:
        cv2.line(frame, (round(map_topleft[0]), round(map_topleft[1])), (round(map_topleft[0]), round(map_bottomright[1])), (0,0,255), setupframelinethickness)
        cv2.line(frame, (round(map_bottomright[0]), round(map_topleft[1])), (round(map_bottomright[0]), round(map_bottomright[1])), (0,0,255), setupframelinethickness)
        cv2.line(frame, (round(map_topleft[0]), round(map_topleft[1])), (round(map_bottomright[0]), round(map_topleft[1])), (0,0,255), setupframelinethickness)
        cv2.line(frame, (round(map_topleft[0]), round(map_bottomright[1])), (round(map_bottomright[0]), round(map_bottomright[1])), (0,0,255), setupframelinethickness)

    if get_arrow_topleft == True:
        cv2.line(frame, (round(original_pixel_x), round(0*frame_height)), (round(original_pixel_x), round(1*frame_height)), (40,130,210), setupframelinethickness)
        cv2.line(frame, (round(0*frame_width), round(original_pixel_y)), (round(1*frame_width), round(original_pixel_y)), (40,130,210), setupframelinethickness)
        cv2.putText(frame, "Arrow Top Left", (round(original_pixel_x-setupframetextsize*120), round(original_pixel_y-setupframetextsize*5)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize/2, (40,130,210), setupframetextthickness, cv2.LINE_AA)
        cv2.putText(frame, f"{round(original_pixel_x), round(original_pixel_y)}", (round(original_pixel_x-setupframetextsize*100), round(original_pixel_y+setupframetextsize*15)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize/2, (40,130,210), setupframetextthickness, cv2.LINE_AA)
    else:
        if arrow_topleft != None:
            xpos, ypos = arrow_topleft
            cv2.line(frame, (round(xpos), round(0*frame_height)), (round(xpos), round(1*frame_height)), (40,130,210), setupframelinethickness)
            cv2.line(frame, (round(0*frame_width), round(ypos)), (round(1*frame_width), round(ypos)), (40,130,210), setupframelinethickness)
            cv2.putText(frame, "Arrow Top Left", (round(xpos-setupframetextsize*120), round(ypos-setupframetextsize*5)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize/2, (40,130,210), setupframetextthickness, cv2.LINE_AA)
            cv2.putText(frame, f"({xpos}, {ypos})", (round(xpos-setupframetextsize*100), round(ypos+setupframetextsize*15)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize/2, (40,130,210), setupframetextthickness, cv2.LINE_AA)

    if get_arrow_bottomright == True:
        cv2.line(frame, (round(original_pixel_x), round(0*frame_height)), (round(original_pixel_x), round(1*frame_height)), (40,130,210), setupframelinethickness)
        cv2.line(frame, (round(0*frame_width), round(original_pixel_y)), (round(1*frame_width), round(original_pixel_y)), (40,130,210), setupframelinethickness)
        cv2.putText(frame, "Arrow Bottom Right", (round(original_pixel_x+setupframetextsize*5), round(original_pixel_y+setupframetextsize*15)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize/2, (40,130,210), setupframetextthickness, cv2.LINE_AA)
        cv2.putText(frame, f"{round(original_pixel_x), round(original_pixel_y)}", (round(original_pixel_x+setupframetextsize*5), round(original_pixel_y-setupframetextsize*5)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize/2, (40,130,210), setupframetextthickness, cv2.LINE_AA)
    else:
        if arrow_bottomright != None:
            xpos, ypos = arrow_bottomright
            cv2.line(frame, (round(xpos), round(0*frame_height)), (round(xpos), round(1*frame_height)), (40,130,210), setupframelinethickness)
            cv2.line(frame, (round(0*frame_width), round(ypos)), (round(1*frame_width), round(ypos)), (40,130,210), setupframelinethickness)
            cv2.putText(frame, "Arrow Bottom Right", (round(xpos+setupframetextsize*5), round(ypos+setupframetextsize*15)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize/2, (40,130,210), setupframetextthickness, cv2.LINE_AA)
            cv2.putText(frame, f"({xpos}, {ypos})", (round(xpos+setupframetextsize*5), round(ypos-setupframetextsize*5)), cv2.FONT_HERSHEY_SIMPLEX, setupframetextsize/2, (40,130,210), setupframetextthickness, cv2.LINE_AA)

    if arrow_topleft != None and arrow_bottomright != None and get_arrow_topleft == False and get_arrow_bottomright == False:
        cv2.line(frame, (round(arrow_topleft[0]), round(arrow_topleft[1])), (round(arrow_topleft[0]), round(arrow_bottomright[1])), (40,255,255), setupframelinethickness)
        cv2.line(frame, (round(arrow_bottomright[0]), round(arrow_topleft[1])), (round(arrow_bottomright[0]), round(arrow_bottomright[1])), (40,255,255), setupframelinethickness)
        cv2.line(frame, (round(arrow_topleft[0]), round(arrow_topleft[1])), (round(arrow_bottomright[0]), round(arrow_topleft[1])), (40,255,255), setupframelinethickness)
        cv2.line(frame, (round(arrow_topleft[0]), round(arrow_bottomright[1])), (round(arrow_bottomright[0]), round(arrow_bottomright[1])), (40,255,255), setupframelinethickness)

    if get_map_topleft == True and left_clicked == True:
        if mouseposx >= button_get_map_top_left[0] and mouseposy >= button_get_map_top_left[1] and mouseposx <= button_get_map_top_left[2] and mouseposy <= button_get_map_top_left[3]:
            pass
        else:
            get_map_topleft = False
            map_topleft = (original_pixel_x, original_pixel_y)
            allowerror = True
            if map_topleft != None and map_bottomright != None:
                if map_topleft[0] > map_bottomright[0] and allowerror == True:
                    messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                    allowerror = False
                if map_topleft[1] > map_bottomright[1] and allowerror == True:
                    messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                    allowerror = False
            if allowerror == True:
                CreateSettings("NavigationDetection", "map_topleft", (round(original_pixel_x), round(original_pixel_y)))
            else:
                map_topleft = GetSettings("NavigationDetection", "map_topleft", "unset")
                if map_topleft == "unset":
                    map_topleft = None

    if get_map_bottomright == True and left_clicked == True:
        if mouseposx >= button_get_map_bottom_right[0] and mouseposy >= button_get_map_bottom_right[1] and mouseposx <= button_get_map_bottom_right[2] and mouseposy <= button_get_map_bottom_right[3]:
            pass
        else:
            get_map_bottomright = False
            map_bottomright = (original_pixel_x, original_pixel_y)
            allowerror = True
            if map_topleft != None and map_bottomright != None:
                if map_topleft[0] > map_bottomright[0] and allowerror == True:
                    messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                    allowerror = False
                if map_topleft[1] > map_bottomright[1] and allowerror == True:
                    messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                    allowerror = False
            if allowerror == True:
                CreateSettings("NavigationDetection", "map_bottomright", (round(original_pixel_x), round(original_pixel_y)))
            else:
                map_bottomright = GetSettings("NavigationDetection", "map_bottomright", "unset")
                if map_bottomright == "unset":
                    map_bottomright = None

    if get_arrow_topleft == True and left_clicked == True:
        if mouseposx >= button_get_arrow_top_left[0] and mouseposy >= button_get_arrow_top_left[1] and mouseposx <= button_get_arrow_top_left[2] and mouseposy <= button_get_arrow_top_left[3]:
            pass
        else:
            get_arrow_topleft = False
            arrow_topleft = (original_pixel_x, original_pixel_y)
            allowerror = True
            if arrow_topleft != None and arrow_bottomright != None:
                if arrow_topleft[0] > arrow_bottomright[0] and allowerror == True:
                    messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                    allowerror = False
                if arrow_topleft[1] > arrow_bottomright[1] and allowerror == True:
                    messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                    allowerror = False
            if allowerror == True:
                CreateSettings("NavigationDetection", "arrow_topleft", (round(original_pixel_x), round(original_pixel_y)))
            else:
                arrow_topleft = GetSettings("NavigationDetection", "arrow_topleft", "unset")
                if arrow_topleft == "unset":
                    arrow_topleft = None

    if get_arrow_bottomright == True and left_clicked == True:
        if mouseposx >= button_get_arrow_bottom_right[0] and mouseposy >= button_get_arrow_bottom_right[1] and mouseposx <= button_get_arrow_bottom_right[2] and mouseposy <= button_get_arrow_bottom_right[3]:
            pass
        else:
            get_arrow_bottomright = False
            arrow_bottomright = (original_pixel_x, original_pixel_y)
            allowerror = True
            if arrow_topleft != None and arrow_bottomright != None:
                if arrow_topleft[0] > arrow_bottomright[0] and allowerror == True:
                    messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                    allowerror = False
                if arrow_topleft[1] > arrow_bottomright[1] and allowerror == True:
                    messagebox.showwarning(title="Setup", message="There is a problem with you setup, do it like it is shown in the example image!")
                    allowerror = False
            if allowerror == True:
                CreateSettings("NavigationDetection", "arrow_bottomright", (round(original_pixel_x), round(original_pixel_y)))
            else:
                arrow_bottomright = GetSettings("NavigationDetection", "arrow_bottomright", "unset")
                if arrow_bottomright == "unset":
                    arrow_bottomright = None

    if corner1 < corner2 and corner3 < corner4:
        frame = frame[corner1:corner2, corner3:corner4]
    else:
        zoom = 0
        zoomoffsetx = 0
        zoomoffsety = 0

    if left_clicked == False:
        moverootx = zoomoffsetx + mousex
        moverooty = zoomoffsety + mousey

    if mouseposx >= 0.0 and mouseposy >= button_area and mouseposx <= 1.0 and mouseposy <= 1.0:
        if left_clicked == True:
            zoomoffsetx = moverootx - mousex
            zoomoffsety = moverooty - mousey

    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    if mouseposx >= button_zoom_in[0] and mouseposy >= button_zoom_in[1] and mouseposx <= button_zoom_in[2] and mouseposy <= button_zoom_in[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_zoom_in[0]*frame_width), round(button_zoom_in[1]*frame_height)), (round(button_zoom_in[2]*frame_width), round(button_zoom_in[3]*frame_height)), (70, 20, 20), -1)
        if left_clicked == True:
            if round(frame_height*zoom/100) < round(frame_height-frame_height*zoom/100) - frame_height/2:
                zoom += 0.3
            if zoom < 0:
                zoom = 0
    else:
        cv2.rectangle(frame, (round(button_zoom_in[0]*frame_width), round(button_zoom_in[1]*frame_height)), (round(button_zoom_in[2]*frame_width), round(button_zoom_in[3]*frame_height)), (50, 0, 0), -1)
    current_text = "Zoom IN"
    width_target_current_text = frame_width/10
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "Zoom IN", (round(button_zoom_in[4]*frame_width), round(button_zoom_in[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

    if mouseposx >= button_zoom_out[0] and mouseposy >= button_zoom_out[1] and mouseposx <= button_zoom_out[2] and mouseposy <= button_zoom_out[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_zoom_out[0]*frame_width), round(button_zoom_out[1]*frame_height)), (round(button_zoom_out[2]*frame_width), round(button_zoom_out[3]*frame_height)), (70, 20, 20), -1)
        if left_clicked == True:
            zoom -= 0.3
            if zoom < 0:
                zoom = 0
    else:
        cv2.rectangle(frame, (round(button_zoom_out[0]*frame_width), round(button_zoom_out[1]*frame_height)), (round(button_zoom_out[2]*frame_width), round(button_zoom_out[3]*frame_height)), (50, 0, 0), -1)
    current_text = "Zoom OUT"
    width_target_current_text = frame_width/10
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "Zoom OUT", (round(button_zoom_out[4]*frame_width), round(button_zoom_out[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

    if mouseposx >= button_new_screenshot[0] and mouseposy >= button_new_screenshot[1] and mouseposx <= button_new_screenshot[2] and mouseposy <= button_new_screenshot[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_new_screenshot[0]*frame_width), round(button_new_screenshot[1]*frame_height)), (round(button_new_screenshot[2]*frame_width), round(button_new_screenshot[3]*frame_height)), (70, 20, 20), -1)
        if left_clicked == False and last_left_clicked == True:
            screenshot = pyautogui.screenshot()
            setupframe = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    else:
        cv2.rectangle(frame, (round(button_new_screenshot[0]*frame_width), round(button_new_screenshot[1]*frame_height)), (round(button_new_screenshot[2]*frame_width), round(button_new_screenshot[3]*frame_height)), (50, 0, 0), -1)
    current_text = "Screenshot"
    width_target_current_text = frame_width/10
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "Screenshot", (round(button_new_screenshot[4]*frame_width), round(button_new_screenshot[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
    textsize_current_text, _ = cv2.getTextSize("Screenshot", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_screenshot_text, height_screenshot_text = textsize_current_text
    textsize_current_text, _ = cv2.getTextSize("New", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_new_text, height_new_text = textsize_current_text
    cv2.putText(frame, "New", (round(button_new_screenshot[4]*frame_width+width_screenshot_text/2-width_new_text/2), round((button_new_screenshot[5]-0.03)*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

    if mouseposx >= button_reset[0] and mouseposy >= button_reset[1] and mouseposx <= button_reset[2] and mouseposy <= button_reset[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_reset[0]*frame_width), round(button_reset[1]*frame_height)), (round(button_reset[2]*frame_width), round(button_reset[3]*frame_height)), (0, 0, 255), -1)
        if left_clicked == True:
            if messagebox.askokcancel("Setup", (f"Do you really want to reset the setup to default settings?")):
                zoom = 0
                zoomoffsetx = 0
                zoomoffsety = 0
                map_topleft = None
                map_bottomright = None
                arrow_topleft = None
                arrow_bottomright = None

                frame = setupframe.copy()
                frame_width = frame.shape[1]
                frame_height = frame.shape[0]
                
                # Code below by Tumppi066
                minimapDistanceFromRight = 27
                minimapDistanceFromBottom = 134
                minimapWidth = 560
                minimapHeight = 293
                scale = frame_height/1440
                xCoord = frame_width - (minimapDistanceFromRight * scale + minimapWidth * scale)
                yCoord = frame_height - (minimapDistanceFromBottom * scale + minimapHeight * scale)
                map_topleft = (int(xCoord), int(yCoord))
                xCoord = frame_width - (minimapDistanceFromRight * scale)
                yCoord = frame_height - (minimapDistanceFromBottom * scale)
                map_bottomright = (int(xCoord), int(yCoord))
                xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.57
                yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.575
                arrow_topleft = (int(xCoord), int(yCoord))
                xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.43
                yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.39
                arrow_bottomright = (int(xCoord), int(yCoord))
                #

                CreateSettings("NavigationDetection", "map_topleft", map_topleft)
                CreateSettings("NavigationDetection", "map_bottomright", map_bottomright)
                CreateSettings("NavigationDetection", "arrow_topleft", arrow_topleft)
                CreateSettings("NavigationDetection", "arrow_bottomright", arrow_bottomright)
    else:
        cv2.rectangle(frame, (round(button_reset[0]*frame_width), round(button_reset[1]*frame_height)), (round(button_reset[2]*frame_width), round(button_reset[3]*frame_height)), (0, 0, 230), -1)
    current_text = "RESET"
    width_target_current_text = frame_width/12
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "RESET", (round(button_reset[4]*frame_width), round(button_reset[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

    if mouseposx >= button_finish[0] and mouseposy >= button_finish[1] and mouseposx <= button_finish[2] and mouseposy <= button_finish[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_finish[0]*frame_width), round(button_finish[1]*frame_height)), (round(button_finish[2]*frame_width), round(button_finish[3]*frame_height)), (0, 235, 0), -1)
        if left_clicked == True:

            if map_topleft != None and map_bottomright != None and arrow_topleft != None and arrow_bottomright != None:
                CreateSettings("bettercam", "x", map_topleft[0])
                CreateSettings("bettercam", "y", map_topleft[1])
                CreateSettings("bettercam", "width", map_bottomright[0] - map_topleft[0])
                CreateSettings("bettercam", "height", map_bottomright[1] - map_topleft[1])
                
                screencap_display = GetSettings("bettercam", "display")
                if screencap_display == None:
                    CreateSettings("bettercam", "display", 0)
                    screencap_display = 0
                screencap_device = GetSettings("bettercam", "device")
                if screencap_device == None:
                    CreateSettings("bettercam", "device", 0)
                    screencap_device = 0
                
                CreateSettings("NavigationDetection", "map_topleft", map_topleft)
                CreateSettings("NavigationDetection", "map_bottomright", map_bottomright)
                CreateSettings("NavigationDetection", "arrow_topleft", arrow_topleft)
                CreateSettings("NavigationDetection", "arrow_bottomright", arrow_bottomright)

                setupframe = setupframe[arrow_topleft[1]:arrow_bottomright[1], arrow_topleft[0]:arrow_bottomright[0]]
                lower_blue = np.array([121, 68, 0])
                upper_blue = np.array([250, 184, 109])
                mask_blue = cv2.inRange(setupframe, lower_blue, upper_blue)
                arrow_height, arrow_width = mask_blue.shape[:2]
                pixel_ratio = round(cv2.countNonZero(mask_blue) / (arrow_width * arrow_height), 3)

                CreateSettings("NavigationDetection", "arrow_percentage", pixel_ratio)

            else:
                # Code below by Tumppi066
                minimapDistanceFromRight = 27
                minimapDistanceFromBottom = 134
                minimapWidth = 560
                minimapHeight = 293
                scale = frame_height/1440
                xCoord = frame_width - (minimapDistanceFromRight * scale + minimapWidth * scale)
                yCoord = frame_height - (minimapDistanceFromBottom * scale + minimapHeight * scale)
                map_topleft = (int(xCoord), int(yCoord))
                xCoord = frame_width - (minimapDistanceFromRight * scale)
                yCoord = frame_height - (minimapDistanceFromBottom * scale)
                map_bottomright = (int(xCoord), int(yCoord))
                xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.57
                yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.575
                arrow_topleft = (int(xCoord), int(yCoord))
                xCoord = map_bottomright[0] - (map_bottomright[0] - map_topleft[0]) * 0.43
                yCoord = map_bottomright[1] - (map_bottomright[1] - map_topleft[1]) * 0.39
                arrow_bottomright = (int(xCoord), int(yCoord))
                #

                CreateSettings("NavigationDetection", "map_topleft", map_topleft)
                CreateSettings("NavigationDetection", "map_bottomright", map_bottomright)
                CreateSettings("NavigationDetection", "arrow_topleft", arrow_topleft)
                CreateSettings("NavigationDetection", "arrow_bottomright", arrow_bottomright)
                CreateSettings("NavigationDetection", "arrow_percentage", "unset")

            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py"), "r+") as file:
                content = file.read()
                file.seek(0)
                if "# this comment is used to reload the app after finishing the setup - 0" in content:
                    content = content.replace("# this comment is used to reload the app after finishing the setup - 0", "# this comment is used to reload the app after finishing the setup - 1")
                else:
                    content = content.replace("# this comment is used to reload the app after finishing the setup - 1", "# this comment is used to reload the app after finishing the setup - 0")
                file.write(content)
                file.truncate()

            try:
                cv2.destroyWindow('Setup')
            except:
                pass
            try:
                cv2.destroyWindow('Example Image')
            except:
                pass

            break

    else:
        cv2.rectangle(frame, (round(button_finish[0]*frame_width), round(button_finish[1]*frame_height)), (round(button_finish[2]*frame_width), round(button_finish[3]*frame_height)), (0, 215, 0), -1)
    current_text = "Finish"
    width_target_current_text = frame_width/15
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "Setup", (round(button_finish[4]*frame_width), round(button_finish[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
    textsize_current_text, _ = cv2.getTextSize("Setup", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_finish_text, height_finish_text = textsize_current_text
    textsize_current_text, _ = cv2.getTextSize("Finish", cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_setup_text, height_setup_text = textsize_current_text
    cv2.putText(frame, "Finish", (round(button_finish[4]*frame_width+width_finish_text/2-width_setup_text/2), round((button_finish[5]-0.04)*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)


    if mouseposx >= button_get_map_top_left[0] and mouseposy >= button_get_map_top_left[1] and mouseposx <= button_get_map_top_left[2] and mouseposy <= button_get_map_top_left[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_get_map_top_left[0]*frame_width), round(button_get_map_top_left[1]*frame_height)), (round(button_get_map_top_left[2]*frame_width), round(button_get_map_top_left[3]*frame_height)), (252, 3, 90), -1)
        if left_clicked == True and get_map_bottomright == False and get_arrow_topleft == False and get_arrow_bottomright == False:
            get_map_topleft = True
    else:
        cv2.rectangle(frame, (round(button_get_map_top_left[0]*frame_width), round(button_get_map_top_left[1]*frame_height)), (round(button_get_map_top_left[2]*frame_width), round(button_get_map_top_left[3]*frame_height)), (232, 0, 70), -1)
    if get_map_topleft == True:
        cv2.rectangle(frame, (round(button_get_map_top_left[0]*frame_width), round(button_get_map_top_left[1]*frame_height)), (round(button_get_map_top_left[2]*frame_width), round(button_get_map_top_left[3]*frame_height)), (232, 0, 170), -1)
    current_text = "Set Top Left Coordinate of Map"
    width_target_current_text = (button_get_map_top_left[2]*frame_width - button_get_map_top_left[0]*frame_width) * button_get_map_top_left[6]
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "Set Top Left Coordinate of Map", (round(button_get_map_top_left[4]*frame_width+(button_get_map_top_left[2]*frame_width-button_get_map_top_left[0]*frame_width)/2-width_current_text/2), round(button_get_map_top_left[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
    

    if mouseposx >= button_get_map_bottom_right[0] and mouseposy >= button_get_map_bottom_right[1] and mouseposx <= button_get_map_bottom_right[2] and mouseposy <= button_get_map_bottom_right[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_get_map_bottom_right[0]*frame_width), round(button_get_map_bottom_right[1]*frame_height)), (round(button_get_map_bottom_right[2]*frame_width), round(button_get_map_bottom_right[3]*frame_height)), (252, 3, 90), -1)
        if left_clicked == True and get_map_topleft == False and get_arrow_topleft == False and get_arrow_bottomright == False:
            get_map_bottomright = True
    else:
        cv2.rectangle(frame, (round(button_get_map_bottom_right[0]*frame_width), round(button_get_map_bottom_right[1]*frame_height)), (round(button_get_map_bottom_right[2]*frame_width), round(button_get_map_bottom_right[3]*frame_height)), (232, 0, 70), -1)
    if get_map_bottomright == True:
        cv2.rectangle(frame, (round(button_get_map_bottom_right[0]*frame_width), round(button_get_map_bottom_right[1]*frame_height)), (round(button_get_map_bottom_right[2]*frame_width), round(button_get_map_bottom_right[3]*frame_height)), (232, 0, 170), -1)
    current_text = "Set Bottom Right Coordinate of Map"
    width_target_current_text = (button_get_map_bottom_right[2]*frame_width - button_get_map_bottom_right[0]*frame_width) * button_get_map_bottom_right[6]
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "Set Bottom Right Coordinate of Map", (round(button_get_map_bottom_right[4]*frame_width+(button_get_map_bottom_right[2]*frame_width-button_get_map_bottom_right[0]*frame_width)/2-width_current_text/2), round(button_get_map_bottom_right[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
    

    if mouseposx >= button_get_arrow_top_left[0] and mouseposy >= button_get_arrow_top_left[1] and mouseposx <= button_get_arrow_top_left[2] and mouseposy <= button_get_arrow_top_left[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_get_arrow_top_left[0]*frame_width), round(button_get_arrow_top_left[1]*frame_height)), (round(button_get_arrow_top_left[2]*frame_width), round(button_get_arrow_top_left[3]*frame_height)), (252, 3, 90), -1)
        if left_clicked == True and get_map_topleft == False and get_map_bottomright == False and get_arrow_bottomright == False:
            get_arrow_topleft = True
    else:
        cv2.rectangle(frame, (round(button_get_arrow_top_left[0]*frame_width), round(button_get_arrow_top_left[1]*frame_height)), (round(button_get_arrow_top_left[2]*frame_width), round(button_get_arrow_top_left[3]*frame_height)), (232, 0, 70), -1)
    if get_arrow_topleft == True:
        cv2.rectangle(frame, (round(button_get_arrow_top_left[0]*frame_width), round(button_get_arrow_top_left[1]*frame_height)), (round(button_get_arrow_top_left[2]*frame_width), round(button_get_arrow_top_left[3]*frame_height)), (232, 0, 170), -1)
    current_text = "Set Top Left Coordinate of Arrow"
    width_target_current_text = (button_get_arrow_top_left[2]*frame_width - button_get_arrow_top_left[0]*frame_width) * button_get_arrow_top_left[6]
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "Set Top Left Coordinate of Arrow", (round(button_get_arrow_top_left[4]*frame_width+(button_get_arrow_top_left[2]*frame_width-button_get_arrow_top_left[0]*frame_width)/2-width_current_text/2), round(button_get_arrow_top_left[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
    

    if mouseposx >= button_get_arrow_bottom_right[0] and mouseposy >= button_get_arrow_bottom_right[1] and mouseposx <= button_get_arrow_bottom_right[2] and mouseposy <= button_get_arrow_bottom_right[3] and mousecoordroot[1] < button_area:
        cv2.rectangle(frame, (round(button_get_arrow_bottom_right[0]*frame_width), round(button_get_arrow_bottom_right[1]*frame_height)), (round(button_get_arrow_bottom_right[2]*frame_width), round(button_get_arrow_bottom_right[3]*frame_height)), (252, 3, 90), -1)
        if left_clicked == True and get_map_topleft == False and get_map_bottomright == False and get_arrow_topleft == False:
            get_arrow_bottomright = True
    else:
        cv2.rectangle(frame, (round(button_get_arrow_bottom_right[0]*frame_width), round(button_get_arrow_bottom_right[1]*frame_height)), (round(button_get_arrow_bottom_right[2]*frame_width), round(button_get_arrow_bottom_right[3]*frame_height)), (232, 0, 70), -1)
    if get_arrow_bottomright == True:
        cv2.rectangle(frame, (round(button_get_arrow_bottom_right[0]*frame_width), round(button_get_arrow_bottom_right[1]*frame_height)), (round(button_get_arrow_bottom_right[2]*frame_width), round(button_get_arrow_bottom_right[3]*frame_height)), (232, 0, 170), -1)
    current_text = "Set Bottom Right Coordinate of Arrow"
    width_target_current_text = (button_get_arrow_bottom_right[2]*frame_width - button_get_arrow_bottom_right[0]*frame_width) * button_get_arrow_bottom_right[6]
    fontscale_current_text = 1
    textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
    width_current_text, height_current_text = textsize_current_text
    max_count_current_text = 3
    while width_current_text != width_target_current_text:
        fontscale_current_text *= width_target_current_text / width_current_text if width_current_text != 0 else 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    fontthickness_current_text = round(fontscale_current_text*2)
    if fontthickness_current_text <= 0:
        fontthickness_current_text = 1
    cv2.putText(frame, "Set Bottom Right Coordinate of Arrow", (round(button_get_arrow_bottom_right[4]*frame_width+(button_get_arrow_bottom_right[2]*frame_width-button_get_arrow_bottom_right[0]*frame_width)/2-width_current_text/2), round(button_get_arrow_bottom_right[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)
    
    last_left_clicked = left_clicked

    cv2.imshow('Setup', frame)
    cv2.imshow('Example Image', exampleimage)
    cv2.waitKey(1)