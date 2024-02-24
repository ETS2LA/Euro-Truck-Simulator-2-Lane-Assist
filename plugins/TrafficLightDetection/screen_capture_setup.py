from tkinter import messagebox
import numpy as np
import ctypes
import mouse
import json
import cv2
import mss
import os


window_name = "TrafficLightDetection - Screen Capture Setup"
example_window_name = "TrafficLightDetection - Example"


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

setupframe = temp_frames[monitor]
empty_frame = np.zeros((setupframe.shape[0], setupframe.shape[1], 3), np.uint8)
frame_width = setupframe.shape[1]
frame_height = setupframe.shape[0]
screen_width = sct.monitors[monitor]["width"]
screen_height = sct.monitors[monitor]["height"]


file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
exampleimage = cv2.imread(file_path + r"\assets\TrafficLightDetection\setupexample.png")
currentProfile = os.path.join(file_path, "profiles", "currentProfile.txt")


exampleimage_width = exampleimage.shape[1]
exampleimage_height = exampleimage.shape[0]
cv2.namedWindow(example_window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(example_window_name, round(frame_width/2.5), round(frame_width/5.93))
cv2.imshow(example_window_name, exampleimage)
cv2.waitKey(1)

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, round(frame_width/2), round(frame_height/2))
cv2.imshow(window_name, setupframe)
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


get_top_left = False
get_bottom_right = False
top_left = GetSettings("TrafficLightDetection", "x1ofsc", 0), GetSettings("TrafficLightDetection", "y1ofsc", 0)
bottom_right = GetSettings("TrafficLightDetection", "x2ofsc", screen_width), GetSettings("TrafficLightDetection", "y2ofsc", round(screen_height/1.5))

last_left_clicked = False


while True:
    frame = setupframe.copy()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, window_name):
        left_clicked = True
    else:
        left_clicked = False

    try:
        _, _, _, _ = cv2.getWindowImageRect(example_window_name)
    except:
        exampleimage_width = exampleimage.shape[1]
        exampleimage_height = exampleimage.shape[0]
        cv2.namedWindow(example_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(example_window_name, round(frame_width/2.5), round(frame_width/5.93))

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

    if get_top_left == False:
        cv2.line(frame, (top_left[0], 0), (top_left[0], screen_height), (0, 0, 150), round(frame_height/270))
        cv2.line(frame, (0, top_left[1]), (screen_width, top_left[1]), (0, 0, 150), round(frame_height/270))
        text, fontscale, thickness, width, height = get_text_size("Top Left", 0.5*frame_width, 0.05*frame_height)
        cv2.putText(frame, text, (round(top_left[0] + height * 0.2), round(top_left[1] + height * 1.2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 255), thickness, cv2.LINE_AA)
    else:
        cv2.line(frame, (round(mouse_x*frame_width), 0), (round(mouse_x*frame_width), screen_height), (0, 0, 150), round(frame_height/270))
        cv2.line(frame, (0, round(mouse_y*frame_height)), (screen_width, round(mouse_y*frame_height)), (0, 0, 150), round(frame_height/270))
        text, fontscale, thickness, width, height = get_text_size("Top Left", 0.5*frame_width, 0.05*frame_height)
        cv2.putText(frame, text, (round(mouse_x*frame_width + height * 0.2), round(mouse_y*frame_height + height * 1.2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 255), thickness, cv2.LINE_AA)

    if get_bottom_right == False:
        cv2.line(frame, (bottom_right[0], 0), (bottom_right[0], screen_height), (0, 0, 150), round(frame_height/270))
        cv2.line(frame, (0, bottom_right[1]), (screen_width, bottom_right[1]), (0, 0, 150), round(frame_height/270))
        text, fontscale, thickness, width, height = get_text_size("Bottom Right", 0.5*frame_width, 0.05*frame_height)
        cv2.putText(frame, text, (round(bottom_right[0] - width - height * 0.2), round(bottom_right[1] - height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 255), thickness, cv2.LINE_AA)
    else:
        cv2.line(frame, (round(mouse_x*frame_width), 0), (round(mouse_x*frame_width), screen_height), (0, 0, 150), round(frame_height/270))
        cv2.line(frame, (0, round(mouse_y*frame_height)), (screen_width, round(mouse_y*frame_height)), (0, 0, 150), round(frame_height/270))
        text, fontscale, thickness, width, height = get_text_size("Bottom Right", 0.5*frame_width, 0.05*frame_height)
        cv2.putText(frame, text, (round(mouse_x*frame_width - width - height * 0.2), round(mouse_y*frame_height - height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 255), thickness, cv2.LINE_AA)

    if get_top_left == False and get_bottom_right == False:
        cv2.rectangle(frame, (top_left[0], top_left[1]), (bottom_right[0], bottom_right[1]), (0, 0, 255), round(frame_height/270))

    if get_top_left == False and get_bottom_right == False:
        finish_setup_pressed, finish_setup_hovered = make_button(text="Finish Setup",
                    x1=0.80*frame_width,
                    y1=0.9*frame_height,
                    x2=1*frame_width,
                    y2=1*frame_height,
                    round_corners=30,
                    buttoncolor=(0, 200, 0),
                    buttonhovercolor=(0, 230, 0),
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
        
        new_screenshot_pressed, new_screenshot_hovered = make_button(text="New Screenshot",
                    x1=0.80*frame_width,
                    y1=0.79*frame_height,
                    x2=1*frame_width,
                    y2=0.89*frame_height,
                    round_corners=30,
                    buttoncolor=(100, 0, 0),
                    buttonhovercolor=(130, 30, 30),
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
        
        if switch_monitor_enabled == True:
            switch_monitor_pressed, switch_monitor_hovered = make_button(text="Switch Monitor",
                    x1=0.80*frame_width,
                    y1=0.68*frame_height,
                    x2=1*frame_width,
                    y2=0.78*frame_height,
                    round_corners=30,
                    buttoncolor=(100, 0, 0),
                    buttonhovercolor=(130, 30, 30),
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
        else:
            switch_monitor_pressed = False
            switch_monitor_hovered = False
    else:
        finish_setup_pressed = False
        finish_setup_hovered = False
        new_screenshot_pressed = False
        new_screenshot_hovered = False
        switch_monitor_pressed = False
        switch_monitor_hovered = False
    
    if get_bottom_right == False and get_top_left == False:
        get_top_left_pressed, get_top_left_hovered = make_button(text="Set Top Left Corner",
                    x1=0.0*frame_width,
                    y1=0.9*frame_height,
                    x2=0.325*frame_width,
                    y2=1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_top_left,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    elif get_top_left == True:
        get_top_left_pressed, get_top_left_hovered = make_button(text="Press on the top left corner of the windshield",
                    x1=0.0*frame_width,
                    y1=0.9*frame_height,
                    x2=1*frame_width,
                    y2=1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_top_left,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    else:
        get_top_left_pressed = False
        get_top_left_hovered = False
    
    if get_top_left == False and get_bottom_right == False:
        get_bottom_right_pressed, get_bottom_right_hovered = make_button(text="Set Bottom Right Corner",
                    x1=0.375*frame_width,
                    y1=0.9*frame_height,
                    x2=0.75*frame_width,
                    y2=1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_bottom_right,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    elif get_bottom_right == True:
        get_bottom_right_pressed, get_bottom_right_hovered = make_button(text="Press on the bottom right corner of the windshield",
                    x1=0.0*frame_width,
                    y1=0.9*frame_height,
                    x2=1*frame_width,
                    y2=1*frame_height,
                    round_corners=30,
                    buttoncolor=(220, 0, 70),
                    buttonhovercolor=(250, 0, 100),
                    buttonselectedcolor=(200, 0, 200),
                    buttonselected=get_bottom_right,
                    textcolor=(255, 255, 255),
                    width_scale=0.9,
                    height_scale=0.9)
    else:
        get_bottom_right_pressed = False
        get_bottom_right_hovered = False
    
    if finish_setup_hovered == True or new_screenshot_hovered == True or get_top_left_hovered == True or get_bottom_right_hovered == True:
        any_hovered = True
    else:
        any_hovered = False

    if finish_setup_pressed == True and get_top_left == False and get_bottom_right == False:
        if top_left[0] < bottom_right[0] and top_left[1] < bottom_right[1]:
            CreateSettings("TrafficLightDetection", "x1ofsc", top_left[0])
            CreateSettings("TrafficLightDetection", "y1ofsc", top_left[1])
            CreateSettings("TrafficLightDetection", "x2ofsc", bottom_right[0])
            CreateSettings("TrafficLightDetection", "y2ofsc", bottom_right[1])
            CreateSettings("bettercam", "display", monitor - 1)
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
                cv2.destroyWindow('Traffic Light Detection - B/W')
            except:
                pass
            try:
                cv2.destroyWindow('Traffic Light Detection - Red/Yellow/Green')
            except:
                pass
            try:
                cv2.destroyWindow('Traffic Light Detection - Final')
            except:
                pass
            break
        else:
            if top_left[0] >= bottom_right[0] and top_left[1] >= bottom_right[1]:
                messagebox.showwarning("TrafficLightDetection", "The Top Left Corner must to the left and above the Bottom Right Corner!\nThe Code will not exit, please try again!")
            elif top_left[0] >= bottom_right[0]:
                messagebox.showwarning("TrafficLightDetection", "The Top Left Corner must to the left of the Bottom Right Corner!\nThe Code will not exit, please try again!")
            elif top_left[1] >= bottom_right[1]:
                messagebox.showwarning("TrafficLightDetection", "The Top Left Corner must to above the Bottom Right Corner!\nThe Code will not exit, please try again!")
            else:
                messagebox.showwarning("TrafficLightDetection", "The Top Left Corner must to the left and above the Bottom Right Corner!\nThe Code will not exit, please try again!")
    
    if new_screenshot_pressed == True:
        setupframe = take_screenshot()
        frame_width = setupframe.shape[1]
        frame_height = setupframe.shape[0]

    if switch_monitor_pressed == True:
        monitor = screen_selection()
        setupframe = take_screenshot()
        frame_width = setupframe.shape[1]
        frame_height = setupframe.shape[0]

    if get_top_left_pressed == True and get_top_left == False and get_bottom_right == False:
        get_top_left = True
    if get_top_left == True and any_hovered == False and left_clicked == False and last_left_clicked == True:
        get_top_left = False
        top_left = round(mouse_x*frame_width), round(mouse_y*frame_height)
    
    if get_bottom_right_pressed == True and get_bottom_right == False and get_top_left == False:
        get_bottom_right = True
    if get_bottom_right == True and any_hovered == False and left_clicked == False and last_left_clicked == True:
        get_bottom_right = False
        bottom_right = round(mouse_x*frame_width), round(mouse_y*frame_height)

    last_left_clicked = left_clicked

    cv2.imshow(example_window_name, exampleimage)
    cv2.imshow(window_name, frame)
    cv2.waitKey(1)