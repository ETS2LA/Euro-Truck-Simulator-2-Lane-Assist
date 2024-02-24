from tkinter import messagebox
import numpy as np
import requests
import pathlib
import ctypes
import mouse
import json
import cv2
import mss
import os


window_name = "NavigationDetection - Automatic Setup"

NORMAL = "\033[0m"
GREEN = "\n\033[92m"
RED = "\033[91m"


sct = mss.mss()

temp_frames = []
for i in range(len(sct.monitors)):
    temp_frames.append((cv2.cvtColor(np.array(sct.grab(sct.monitors[i])), cv2.COLOR_BGRA2BGR)))

monitor = sct.monitors[1]
screen_width = monitor["width"]
screen_height = monitor["height"]

all_monitors_screenshot = cv2.cvtColor(np.array(sct.grab(sct.monitors[0])), cv2.COLOR_BGRA2BGR)
empty_frame = np.zeros((screen_height, screen_width, 3), np.uint8)
frame_width = empty_frame.shape[1]
frame_height = empty_frame.shape[0]

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, round(screen_width/2), round(screen_height/2))
cv2.imshow(window_name, empty_frame)
cv2.waitKey(1)


def get_text_size(text="NONE", text_width=0.5*frame_width, max_text_height=0.5*frame_height):
    fontscale = 1
    textsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)
    width_current_text, height_current_text = textsize
    max_count_current_text = 3
    while width_current_text != text_width or height_current_text > max_text_height:
        fontscale *= min(text_width / textsize[0], max_text_height / textsize[1])
        textsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    thickness = round(fontscale * 2)
    if thickness <= 0:
        thickness = 1
    return text, fontscale, thickness, textsize[0], textsize[1]


def make_button(text="NONE", x1=0, y1=0, x2=100, y2=100, round_corners=30, buttoncolor=(100, 100, 100), buttonhovercolor=(130, 130, 130), buttonselectedcolor=(160, 160, 160), buttonselected=False, textcolor=(255, 255, 255), width_scale=0.9, height_scale=0.8):
    if x1 <= mouse_x*frame_width <= x2 and y1 <= mouse_y*frame_height <= y2:
        buttonhovered = True
    else:
        buttonhovered = False
    if buttonselected == True:
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttonselectedcolor, round_corners)
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttonselectedcolor, -1)
    elif buttonhovered == True:
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttonhovercolor, round_corners)
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttonhovercolor, -1)
    else:
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttoncolor, round_corners)
        cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), buttoncolor, -1)
    text, fontscale, thickness, width, height = get_text_size(text, round((x2-x1)*width_scale), round((y2-y1)*height_scale))
    cv2.putText(frame, text, (round(x1 + (x2-x1) / 2 - width / 2), round(y1 + (y2-y1) / 2 + height / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, textcolor, thickness, cv2.LINE_AA)
    if x1 <= mouse_x*frame_width <= x2 and y1 <= mouse_y*frame_height <= y2 and left_clicked == False and last_left_clicked == True:
        return True, buttonhovered
    else:
        return False, buttonhovered
    

def make_label(text="NONE", x1=0, y1=0, x2=100, y2=100, round_corners=30, labelcolor=(100, 100, 100), textcolor=(255, 255, 255), width_scale=0.9, height_scale=0.8):
    cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), labelcolor, round_corners)
    cv2.rectangle(frame, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), labelcolor, -1)
    lines = text.split('\n')
    lowest_height = None
    for i in range(len(lines)):
        text, fontscale, thickness, width, height = get_text_size(lines[i], round((x2 - x1) * width_scale), frame_height)
        if lowest_height == None or lowest_height > height:
            lowest_height = height
    text_height = lowest_height
    for i in range(len(lines)):
        text, fontscale, thickness, width, height = get_text_size(lines[i], round((x2 - x1) * width_scale), text_height * height_scale)
        cv2.putText(frame, text, (round(x1 + (x2-x1) / 2 - width / 2), round(y1 + (y2 - y1) * ((i + 1) / (len(lines) + 1)) + text_height * height_scale / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, textcolor, thickness, cv2.LINE_AA)


def make_loading_screen(text="NONE", color=(255, 255, 255), text_width=0.5*frame_width, max_text_height=0.5*frame_height):
    frame = empty_frame.copy()
    try:
        _, _, _, _ = cv2.getWindowImageRect(window_name)
    except:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))
    text, fontscale, thickness, width, height = get_text_size(text, text_width, max_text_height)
    cv2.putText(frame, text, (round(frame_width / 2 - width / 2), round(frame_height / 2 + height / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, color, thickness, cv2.LINE_AA)
    cv2.imshow(window_name, frame)
    cv2.waitKey(1)


def screen_selection():
    last_left_clicked = False
    while True:
        frame = empty_frame.copy()
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]

        if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, window_name):
            left_clicked = True
        else:
            left_clicked = False

        try:
            window_x, window_y, window_width, window_height = cv2.getWindowImageRect(window_name)
            mouse_x, mouse_y = mouse.get_position()
            mouse_relative_window = mouse_x-window_x, mouse_y-window_y
            last_window_size = (window_x, window_y, window_width, window_height)
            last_mouse_position = (mouse_x, mouse_y)
        except:
            try:
                window_x, window_y, window_width, window_height = last_window_size
            except:
                window_x, window_y, window_width, window_height = (0, 0, 100, 100)
            try:
                mouse_x, mouse_y = last_mouse_position
            except:
                mouse_x, mouse_y = (0, 0)
            mouse_relative_window = mouse_x-window_x, mouse_y-window_y
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))

        if window_width != 0 and window_height != 0:
            mouse_x = mouse_relative_window[0]/window_width
            mouse_y = mouse_relative_window[1]/window_height
        else:
            mouse_x = 0
            mouse_y = 0

        text, fontscale, thickness, width, height = get_text_size("Select the screen to use:", round(0.9*frame_width), round(0.05*frame_height))

        cv2.putText(frame, text, (round(frame_width / 2 - width / 2), round(0.05*frame_height + height / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (255, 255, 255), thickness, cv2.LINE_AA)
        
        screenshot_height, screenshot_width = all_monitors_screenshot.shape[:2]
        aspect_ratio = screenshot_width / screenshot_height

        target_height = int(0.88 * frame_height)
        target_width = int(target_height * aspect_ratio)

        if target_width > frame_width * 0.98:
            target_width = int(frame_width * 0.98)
            target_height = int(target_width / aspect_ratio)

        resized_screenshot = cv2.resize(all_monitors_screenshot, (target_width, target_height))

        x_offset = (frame_width - target_width) // 2
        y_offset = int(0.11 * frame_height) + ((int(0.88 * frame_height) - target_height) // 2)

        frame[y_offset:y_offset+target_height, x_offset:x_offset+target_width] = resized_screenshot

        for index, monitor in enumerate(sct.monitors[1:], 1):
            monitor_x = monitor["left"] - sct.monitors[0]["left"]
            monitor_y = monitor["top"] - sct.monitors[0]["top"]
            monitor_width = monitor["width"]
            monitor_height = monitor["height"]

            monitor_x_frame = x_offset + int(monitor_x * (target_width / screenshot_width))
            monitor_y_frame = y_offset + int(monitor_y * (target_height / screenshot_height))
            monitor_width_frame = int(monitor_width * (target_width / screenshot_width))
            monitor_height_frame = int(monitor_height * (target_height / screenshot_height))

            top_left_corner = (monitor_x_frame, monitor_y_frame)
            bottom_right_corner = (monitor_x_frame + monitor_width_frame, monitor_y_frame + monitor_height_frame)

            text, fontscale, thickness, width, height = get_text_size(f"Monitor {index}", round(monitor_width_frame * 0.3), round(monitor_height_frame * 0.3))
            cv2.rectangle(frame, (round(monitor_x_frame + monitor_width_frame / 2 - width / 2), round(monitor_y_frame + monitor_height_frame / 2 + height)), (round(monitor_x_frame + monitor_width_frame / 2 + width / 2), round(monitor_y_frame + monitor_height_frame / 2 - height)), (0, 0, 0), height)
            cv2.rectangle(frame, (round(monitor_x_frame + monitor_width_frame / 2 - width / 2), round(monitor_y_frame + monitor_height_frame / 2 + height)), (round(monitor_x_frame + monitor_width_frame / 2 + width / 2), round(monitor_y_frame + monitor_height_frame / 2 - height)), (0, 0, 0), -1)
            cv2.putText(frame, text, (round(monitor_x_frame + monitor_width_frame / 2 - width / 2), round(monitor_y_frame + monitor_height_frame / 2 + height / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (255, 255, 255), thickness, cv2.LINE_AA)
            cv2.rectangle(frame, top_left_corner, bottom_right_corner, (0, 0, 255), thickness)

            if top_left_corner[0] < mouse_x * frame_width < bottom_right_corner[0] and top_left_corner[1] < mouse_y * frame_height < bottom_right_corner[1]:
                cv2.rectangle(frame, (round(top_left_corner[0] + round(0.008 * frame_height)), round(top_left_corner[1] + round(0.008 * frame_height))), (round(bottom_right_corner[0] - round(0.008 * frame_height)), round(bottom_right_corner[1] - round(0.008 * frame_height))), (0, 0, 255), round(0.016 * frame_height))
                if left_clicked == False and last_left_clicked == True:
                    return index
                
        last_left_clicked = left_clicked
                
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)


def take_screenshot():
    screenshot = cv2.cvtColor(np.array(sct.grab(sct.monitors[monitor])), cv2.COLOR_BGRA2BGR)
    return screenshot


if len(sct.monitors) > 2:
    monitor = screen_selection()
    switch_monitor_enabled = True
else:
    monitor = 1
    switch_monitor_enabled = False

screenshot = temp_frames[monitor]
empty_frame = np.zeros((screenshot.shape[0], screenshot.shape[1], 3), np.uint8)
frame_width = screenshot.shape[1]
frame_height = screenshot.shape[0]
screen_width = sct.monitors[monitor]["width"]
screen_height = sct.monitors[monitor]["height"]


file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
currentProfile = os.path.join(file_path, "profiles", "currentProfile.txt")


cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))


print(NORMAL + f"Loading..." + NORMAL)
make_loading_screen("Loading...")


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


folder_path = os.path.dirname(__file__)
modelfile_path = os.path.join(folder_path, "YOLOv5_MapDetectionModel.pt")
last_progress = 0


if not os.path.exists(modelfile_path):
    print(NORMAL + f"Downloading the MapDetection..." + NORMAL)
    make_loading_screen("Downloading the MapDetection...")
    url = "https://huggingface.co/Glas42/MapDetection-YOLOv5/resolve/main/model/YOLOv5_MapDetectionModel.pt?download=true"
    response = requests.get(url, stream=True)
    try:
        with open(modelfile_path, "wb") as modelfile:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            chunk_size = 1024
            for data in response.iter_content(chunk_size=chunk_size):
                downloaded_size += len(data)
                modelfile.write(data)
                progress = (downloaded_size / total_size) * 100
                if round(last_progress) < round(progress):
                    progress_mb = downloaded_size / (1024 * 1024)
                    total_size_mb = total_size / (1024 * 1024)
                    print(f"\rDownloading the MapDetection: {progress:.0f}% ({progress_mb:.2f}MB of {total_size_mb:.2f}MB)", end="", flush=True)
                    make_loading_screen(f"Downloading the MapDetection: {progress:.0f}% ({progress_mb:.2f}MB of {total_size_mb:.2f}MB)", text_width=0.75*frame_width)
                    last_progress = progress
        print(GREEN + f"Successfully downloaded the MapDetection!" + NORMAL)
        make_loading_screen("Successfully downloaded the MapDetection!", color=(0, 255, 0))
    except Exception as e:
        print(RED + f"Failed to download the MapDetection: " + NORMAL + str(e))
        make_loading_screen("Failed to download the MapDetection!", color=(0, 0, 255))
else:
    print(NORMAL + f"The MapDetection is already downloaded!" + NORMAL)
    make_loading_screen("The MapDetection is already downloaded!", (0, 255, 0))


print(NORMAL + f"Loading the MapDetection..." + NORMAL)
make_loading_screen("Loading the MapDetection...")


try:
    pathlib.PosixPath = pathlib.WindowsPath
    import torch
    try:
        torch.hub.set_dir(f"{folder_path}\\YOLOFiles")
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=modelfile_path)
    except:
        torch.hub.set_dir(f"{folder_path}\\YOLOFiles")
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=modelfile_path, force_reload=True)
    print(GREEN + f"Successfully loaded the MapDetection!" + NORMAL)
    make_loading_screen("Successfully loaded the MapDetection!", color=(0, 255, 0))
except Exception as e:
    print(RED + f"Failed to load the MapDetection: " + NORMAL + str(e))
    make_loading_screen("Failed to load the MapDetection!", color=(0, 0, 255))


print(NORMAL + f"Loading..." + NORMAL)
make_loading_screen("Loading...")


last_left_clicked = False
do_detection = False
do_confirmation = False
confirmation_count = 10
coordinates = []


while True:
    frame = screenshot.copy()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, window_name):
        left_clicked = True
    else:
        left_clicked = False

    try:
        window_x, window_y, window_width, window_height = cv2.getWindowImageRect(window_name)
        mouse_x, mouse_y = mouse.get_position()
        mouse_relative_window = mouse_x-window_x, mouse_y-window_y
        last_window_size = (window_x, window_y, window_width, window_height)
        last_mouse_position = (mouse_x, mouse_y)
    except:
        try:
            window_x, window_y, window_width, window_height = last_window_size
        except:
            window_x, window_y, window_width, window_height = (0, 0, 100, 100)
        try:
            mouse_x, mouse_y = last_mouse_position
        except:
            mouse_x, mouse_y = (0, 0)
        mouse_relative_window = mouse_x-window_x, mouse_y-window_y
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))

    if window_width != 0 and window_height != 0:
        mouse_x = mouse_relative_window[0]/window_width
        mouse_y = mouse_relative_window[1]/window_height
    else:
        mouse_x = 0
        mouse_y = 0

    
    if do_detection == False and do_confirmation == False:
        
        make_label("Make sure that the route advisor is visible in the screenshot below and fully zoomed in.\nIf the game minimizes when switch to this window, disable the fullscreen mode in your game.",
                        x1=0.01*frame_width,
                        y1=0.02*frame_height,
                        x2=0.99*frame_width,
                        y2=0.22*frame_height,
                        round_corners=30,
                        labelcolor=(50, 50, 50),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.95)

        button_continue_pressed, button_continue_hovered = make_button(text="Continue",
                        x1=0.505*frame_width,
                        y1=0.24*frame_height,
                        x2=0.99*frame_width,
                        y2=0.34*frame_height,
                        round_corners=30,
                        buttoncolor=(0, 80, 0),
                        buttonhovercolor=(20, 100, 20),
                        buttonselectedcolor=(20, 100, 20),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.5)
        
        button_exit_setup_pressed, button_exit_setup_hovered = make_button(text="Exit Setup",
                        x1=0.01*frame_width,
                        y1=0.24*frame_height,
                        x2=0.495*frame_width,
                        y2=0.34*frame_height,
                        round_corners=30,
                        buttoncolor=(0, 0, 80),
                        buttonhovercolor=(20, 20, 100),
                        buttonselectedcolor=(20, 20, 100),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.5)
        
        button_new_screenshot_pressed, button_new_screenshot_hovered = make_button(text="New Screenshot",
                        x1=0.505*frame_width,
                        y1=0.36*frame_height,
                        x2=0.99*frame_width,
                        y2=0.46*frame_height,
                        round_corners=30,
                        buttoncolor=(80, 0, 0),
                        buttonhovercolor=(100, 20, 20),
                        buttonselectedcolor=(100, 20, 20),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.5)
        
        button_switch_monitor_pressed, button_switch_monitor_hovered = make_button(text="Switch Monitor",
                        x1=0.01*frame_width,
                        y1=0.36*frame_height,
                        x2=0.495*frame_width,
                        y2=0.46*frame_height,
                        round_corners=30,
                        buttoncolor=(80, 0, 0),
                        buttonhovercolor=(100, 20, 20),
                        buttonselectedcolor=(100, 20, 20),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.5)
        
        if button_continue_pressed == True:
            do_detection = True

        if button_exit_setup_pressed == True:
            exit()

        if button_new_screenshot_pressed == True:
            screenshot = take_screenshot()

        if button_switch_monitor_pressed == True:
            monitor = screen_selection()
            screenshot = temp_frames[monitor]
            empty_frame = np.zeros((screenshot.shape[0], screenshot.shape[1], 3), np.uint8)
            frame_width = screenshot.shape[1]
            frame_height = screenshot.shape[0]
            screen_width = sct.monitors[monitor]["width"]
            screen_height = sct.monitors[monitor]["height"]
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))


    if do_detection == True:
        if len(coordinates) < confirmation_count:

            frame = take_screenshot()

            try:
                temp = sct.monitors[monitor]
                left = temp["left"]
                top = temp["top"]
                x1, y1, width, height = cv2.getWindowImageRect(window_name)
                x1 -= left
                y1 -= top
                cv2.rectangle(frame, (x1, y1), (x1+width, y1+height), (0, 0, 0), -1)
            except:
                pass

            make_label(f"Searching for a route advisor, please wait...\nIt could happen that this window will be unresponsive.\nProgress: {len(coordinates)+1} of {confirmation_count}",
                            x1=0.01*frame_width,
                            y1=0.02*frame_height,
                            x2=0.99*frame_width,
                            y2=0.22*frame_height,
                            round_corners=30,
                            labelcolor=(50, 50, 50),
                            textcolor=(255, 255, 255),
                            width_scale=0.95,
                            height_scale=0.65)
        
            button_exit_setup_pressed, button_exit_setup_hovered = make_button(text="Exit Setup",
                            x1=0.01*frame_width,
                            y1=0.24*frame_height,
                            x2=0.255*frame_width,
                            y2=0.34*frame_height,
                            round_corners=30,
                            buttoncolor=(0, 0, 80),
                            buttonhovercolor=(20, 20, 100),
                            buttonselectedcolor=(20, 20, 100),
                            textcolor=(255, 255, 255),
                            width_scale=0.95,
                            height_scale=0.5)

            found_map = False
            found_arrow = False
            map_coords = None
            arrow_coords = None
            max_map_score = 0
            max_arrow_score = 0

            results = model(frame)
            boxes = results.pandas().xyxy[0]
            for _, box in boxes.iterrows():
                label = box['name']
                score = box['confidence']
                x, y, w, h = int(box['xmin']), int(box['ymin']), int(box['xmax'] - box['xmin']), int(box['ymax'] - box['ymin'])
                
                if label == 'map' and score > max_map_score:
                    max_map_score = score
                    map_coords = (x, y, x + w, y + h)

                if label == 'arrow' and score > max_arrow_score:
                    max_arrow_score = score
                    arrow_coords = (x, y, x + w, y + h)

            if map_coords is not None:
                found_map = True
                cv2.rectangle(frame, (map_coords[0], map_coords[1]), (map_coords[2], map_coords[3]), (0, 255, 255), round((map_coords[3] - map_coords[1]) * 0.01))
                text, fontscale, thickness, width, height = get_text_size(f"Map", map_coords[2] - map_coords[0], round((map_coords[3] - map_coords[1]) * 0.15))
                cv2.putText(frame, text, (round((map_coords[0] + map_coords[2]) / 2 - width / 2), round(map_coords[1] - height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 255, 255), thickness, cv2.LINE_AA)

            if arrow_coords is not None and map_coords is not None:
                found_arrow = True
                cv2.rectangle(frame, (arrow_coords[0], arrow_coords[1]), (arrow_coords[2], arrow_coords[3]), (255, 0, 0), round((map_coords[3] - map_coords[1]) * 0.01))
                text, fontscale, thickness, width, height = get_text_size(f"Arrow", map_coords[2] - map_coords[0], round((map_coords[3] - map_coords[1]) * 0.15))
                cv2.putText(frame, text, (round((arrow_coords[0] + arrow_coords[2]) / 2 - width / 2), round(arrow_coords[1] - height * 0.25)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (255, 0, 0), thickness, cv2.LINE_AA)

            if found_arrow == True and found_map == True:
                if map_coords[0] < arrow_coords[0] and map_coords[2] > arrow_coords[2] and map_coords[1] < arrow_coords[1] and map_coords[3] > arrow_coords[3]:
                    coordinates.append((map_coords[0], map_coords[1], map_coords[2], map_coords[3], arrow_coords[0], arrow_coords[1], arrow_coords[2], arrow_coords[3]))
            
            if button_exit_setup_pressed == True:
                exit()

        else:

            make_label(f"Searching for a route advisor, please wait...\nIt could happen that this window will be unresponsive.\nProgress: {confirmation_count} of {confirmation_count}",
                            x1=0.01*frame_width,
                            y1=0.02*frame_height,
                            x2=0.99*frame_width,
                            y2=0.22*frame_height,
                            round_corners=30,
                            labelcolor=(50, 50, 50),
                            textcolor=(255, 255, 255),
                            width_scale=0.95,
                            height_scale=1.0)

            do_detection = False
            do_confirmation = True

            map_x1_sum = 0
            map_y1_sum = 0
            map_x2_sum = 0
            map_y2_sum = 0
            arrow_x1_sum = 0
            arrow_y1_sum = 0
            arrow_x2_sum = 0
            arrow_y2_sum = 0

            for i in range(len(coordinates)):
                map_x1_sum += coordinates[i][0]
                map_y1_sum += coordinates[i][1]
                map_x2_sum += coordinates[i][2]
                map_y2_sum += coordinates[i][3]
                arrow_x1_sum += coordinates[i][4]
                arrow_y1_sum += coordinates[i][5]
                arrow_x2_sum += coordinates[i][6]
                arrow_y2_sum += coordinates[i][7]

            map_x1 = round(map_x1_sum / len(coordinates))
            map_y1 = round(map_y1_sum / len(coordinates))
            map_x2 = round(map_x2_sum / len(coordinates))
            map_y2 = round(map_y2_sum / len(coordinates))
            arrow_x1 = round(arrow_x1_sum / len(coordinates))
            arrow_y1 = round(arrow_y1_sum / len(coordinates))
            arrow_x2 = round(arrow_x2_sum / len(coordinates))
            arrow_y2 = round(arrow_y2_sum / len(coordinates))

            screenshot = take_screenshot()
            temp_screenshot = screenshot.copy()
            frame_width = screenshot.shape[1]
            frame_height = screenshot.shape[0]

            cv2.rectangle(screenshot, (map_x1, map_y1), (map_x2, map_y2), (0, 255, 255), round((map_y2 - map_y1) * 0.01))
            text, fontscale, thickness, width, height = get_text_size(f"Map", map_x2 - map_x1, round((map_y2 - map_y1) * 0.15))
            cv2.putText(screenshot, text, (round((map_x1 + map_x2) / 2 - width / 2), round(map_y1 - height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 255, 255), thickness, cv2.LINE_AA)

            cv2.rectangle(screenshot, (arrow_x1, arrow_y1), (arrow_x2, arrow_y2), (255, 0, 0), round((map_y2 - map_y1) * 0.01))
            text, fontscale, thickness, width, height = get_text_size(f"Arrow", map_x2 - map_x1, round((map_y2 - map_y1) * 0.15))
            cv2.putText(screenshot, text, (round((arrow_x1 + arrow_x2) / 2 - width / 2), round(arrow_y1 - height * 0.25)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (255, 0, 0), thickness, cv2.LINE_AA)

            offset_distance = None

            x1 = round(map_x1 - (map_x2 - map_x1) * 0.3)
            if x1 < 0:
                if offset_distance == None or offset_distance > x1:
                    offset_distance = x1

            x2 = round(map_x2 + (map_x2 - map_x1) * 0.3)
            if x2 > frame_width - 1:
                if offset_distance == None or offset_distance > x2 - (frame_width - 1):
                    offset_distance = (frame_width - 1) - map_x2

            y1 = round(map_y1 - (map_y2 - map_y1) * 0.5)
            if y1 < 0:
                if offset_distance == None or offset_distance > y1  * 3:
                    offset_distance = y1
                
            y2 = round(map_y2 + (map_y2 - map_y1) * 0.3)
            if y2 > frame_height - 1:
                if offset_distance == None or offset_distance > y2 - (frame_height - 1):
                    offset_distance = (frame_height - 1) - map_y2
            
            if offset_distance != None:
                x1 = map_x1 - offset_distance
                x2 = map_x2 + offset_distance
                y1 = map_y1 - offset_distance
                y2 = map_y2 + offset_distance

            mask = np.zeros_like(screenshot, dtype=np.uint8)
            round_corners = 30
            cv2.rectangle(mask, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), (255, 255, 255), round_corners)
            cv2.rectangle(mask, (round(x1+round_corners/2), round(y1+round_corners/2)), (round(x2-round_corners/2), round(y2-round_corners/2)), (255, 255, 255), -1)
            screenshot = cv2.bitwise_and(screenshot, mask)

            resultsframe = screenshot[y1:y2, x1:x2]
            results_frame_width = resultsframe.shape[1]
            results_frame_height = resultsframe.shape[0]
            aspect_ratio = results_frame_width / results_frame_height
            new_height = int(0.62 * frame_height)
            new_width = int(aspect_ratio * new_height)
            resultsframe = cv2.resize(resultsframe, (new_width, new_height))
            start_x = (frame_width - new_width) // 2
            start_y = round(frame_height - new_height - 0.02 * frame_height)


    if do_confirmation == True:
        frame = empty_frame.copy()

        frame[start_y:start_y+new_height, start_x:start_x+new_width] = resultsframe

        make_label(f"Found the route advisor and arrow position!\nAre the bounding boxes precise enough?",
                        x1=0.01*frame_width,
                        y1=0.02*frame_height,
                        x2=0.99*frame_width,
                        y2=0.22*frame_height,
                        round_corners=30,
                        labelcolor=(50, 50, 50),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.65)
        
        button_exit_setup_pressed, button_exit_setup_hovered = make_button(text="No, Exit Setup",
                        x1=0.01*frame_width,
                        y1=0.24*frame_height,
                        x2=0.33166*frame_width,
                        y2=0.34*frame_height,
                        round_corners=30,
                        buttoncolor=(0, 0, 80),
                        buttonhovercolor=(20, 20, 100),
                        buttonselectedcolor=(20, 20, 100),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.5)
        
        button_try_again_pressed, button_try_again_hovered = make_button(text="No, Try Again",
                        x1=0.34166*frame_width,
                        y1=0.24*frame_height,
                        x2=0.65833*frame_width,
                        y2=0.34*frame_height,
                        round_corners=30,
                        buttoncolor=(0, 80, 80),
                        buttonhovercolor=(20, 100, 100),
                        buttonselectedcolor=(20, 100, 100),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.5)
        
        button_finish_setup_pressed, button_finish_setup_hovered = make_button(text="Yes, Finish Setup",
                        x1=0.66833*frame_width,
                        y1=0.24*frame_height,
                        x2=0.99*frame_width,
                        y2=0.34*frame_height,
                        round_corners=30,
                        buttoncolor=(0, 80, 0),
                        buttonhovercolor=(20, 100, 20),
                        buttonselectedcolor=(20, 100, 20),
                        textcolor=(255, 255, 255),
                        width_scale=0.95,
                        height_scale=0.5)
        
        if button_exit_setup_pressed == True:
            exit()

        if button_try_again_pressed == True:
            do_confirmation = False
            do_detection = False
            coordinates = []
            screenshot = temp_frames[monitor]

        if button_finish_setup_pressed == True:
                
            CreateSettings("bettercam", "x", map_x1)
            CreateSettings("bettercam", "y", map_y1)
            CreateSettings("bettercam", "width", map_x2 - map_x1)
            CreateSettings("bettercam", "height", map_y2 - map_y1)
            
            CreateSettings("bettercam", "display", monitor - 1)
            
            CreateSettings("NavigationDetection", "map_topleft", (map_x1, map_y1))
            CreateSettings("NavigationDetection", "map_bottomright", (map_x2, map_y2))
            CreateSettings("NavigationDetection", "arrow_topleft", (arrow_x1, arrow_y1))
            CreateSettings("NavigationDetection", "arrow_bottomright", (arrow_x2, arrow_y2))

            frame = temp_screenshot[arrow_y1:arrow_y2, arrow_x1:arrow_x2]
            lower_blue = np.array([121, 68, 0])
            upper_blue = np.array([250, 184, 109])
            mask_blue = cv2.inRange(frame, lower_blue, upper_blue)
            arrow_height, arrow_width = mask_blue.shape[:2]
            pixel_ratio = round(cv2.countNonZero(mask_blue) / (arrow_width * arrow_height), 3)

            CreateSettings("NavigationDetection", "arrow_percentage", pixel_ratio)

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
                cv2.destroyWindow(window_name)
            except:
                pass

            break
    

    last_left_clicked = left_clicked


    cv2.imshow(window_name, frame)
    cv2.waitKey(1)