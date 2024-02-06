import numpy as np
import pyautogui
import requests
import pathlib
import ctypes
import torch
import mouse
import json
import cv2
import os

screenshot = pyautogui.screenshot()
setupframe = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
game_frame = setupframe.copy()
frame_width = setupframe.shape[1]
frame_height = setupframe.shape[0]

def startscreen(text="Loading...", color=(255, 255, 255)):
    current_text = text
    width_target_current_text = 0.75*frame_width
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
    cv2.putText(startframe, current_text, (round(frame_width/2-width_current_text/2), round(frame_height/2+height_current_text/2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, color, thickness_current_text, cv2.LINE_AA) 
    cv2.imshow('Setup', startframe)
    cv2.waitKey(1)
startscreen("Loading...")

everything_ok = True
last_progress = 0

file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
currentProfile = os.path.join(file_path, "profiles", "currentProfile.txt")

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

folder = os.path.dirname(__file__)
modelfile_path = os.path.join(folder, "YOLOv5_MapDetectionModel.pt")

if not os.path.exists(modelfile_path):
    print("\033[92m" + f"Downloading the YOLOv5_MapDetectionModel.pt model..." + "\033[0m")
    startscreen("Downloading model...")
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
                    print(f"\rDownload progress: {progress:.0f}% ({progress_mb:.2f} MB of {total_size_mb:.2f} MB)", end="", flush=True)
                    startscreen(f"Downloading Setup Model: {progress:.0f}% ({progress_mb:.2f} MB of {total_size_mb:.2f} MB)")
                    last_progress = progress
        print("\n\033[92m" + f"Successfully downloaded the YOLOv5_MapDetectionModel.pt model!" + "\033[0m")
        startscreen("Download successful!", (0,255,0))
    except Exception as e:
        print("\033[91m" + f"Failed to download the YOLOv5_MapDetectionModel.pt model: " + "\033[0m" + str(e))
        startscreen("Download failed!", (0,0,255))
        everything_ok = False
else:
    print("\033[92m" + f"The YOLOv5_MapDetectionModel.pt model is already downloaded!" + "\033[0m")
    startscreen("Setup model already downloaded!", (0,255,0))

print("\033[92m" + f"Loading the YOLOv5_MapDetectionModel.pt model..." + "\033[0m")
startscreen("Loading setup model...")
try:
    pathlib.PosixPath = pathlib.WindowsPath
    folder_path = os.path.dirname(__file__)
    model_path = os.path.join(folder_path, 'YOLOv5_MapDetectionModel.pt')
    try:
        torch.hub.set_dir(f"{folder_path}\\YoloFiles")
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
    except:
        torch.hub.set_dir(f"{folder_path}\\YoloFiles")
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
    print("\033[92m" + f"Successfully loaded the YOLOv5_MapDetectionModel.pt model!" + "\033[0m")
    startscreen("Setup model successfully loaded!", (0,255,0))
except Exception as e:
    print("\033[91m" + f"Failed to load the YOLOv5_MapDetectionModel.pt model: " + "\033[0m" + str(e))
    startscreen("Failed to load model!", (0,0,255))
    everything_ok = False

if everything_ok == False:
    exit()

red_normal = (0, 0, 100)
red_hover = (0, 0, 120)
green_normal = (0, 100, 0)
green_hover = (0, 120, 0)
blue_normal = (100, 0, 0)
blue_hover = (120, 0, 0)
orange_normal = (0, 50, 100)
orange_hover = (0, 60, 120)

setupframe = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
screenshot = pyautogui.screenshot()
game_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
game_frame_width = setupframe.shape[1]
game_frame_height = setupframe.shape[0]
allow_detection = False
confirmation_count = 12
coordinates = []

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
        cv2.namedWindow('Setup', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Setup', round(frame_width/2), round(frame_height/2))
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

    if width != 0 and height != 0:
        mouseposx = mousex/width
        mouseposy = mousey/height
    else:
        mouseposx = 0
        mouseposy = 0
    
    if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and ctypes.windll.user32.GetForegroundWindow() == ctypes.windll.user32.FindWindowW(None, 'Setup'):
        mouse_left_clicked = True
    else:
        mouse_left_clicked = False

    
    if allow_detection == False:
        current_text = 'Make sure the the minimap is FULLY ZOOMED IN AND VISIBLE at the bottom of this preview.'
        width_target_current_text = 0.95*frame_width
        max_height_current_text = 0.025*frame_height
        fontscale_current_text = 1
        textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
        width_current_text, height_current_text = textsize_current_text
        max_count_current_text = 3
        while width_current_text != width_target_current_text or height_current_text > max_height_current_text:
            fontscale_current_text *= min(width_target_current_text / width_current_text, max_height_current_text / height_current_text)
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text -= 1
            if max_count_current_text <= 0:
                break
        width_title_text, height_title_text = textsize_current_text
        thickness_current_text = round(fontscale_current_text * 2)
        if thickness_current_text <= 0:
            thickness_current_text = 1
        cv2.rectangle(frame, (0, 0), (round(frame_width), round(height_title_text*8)), (0, 0, 0), -1)
        cv2.putText(frame, current_text, (round(height_current_text), round(height_current_text*2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA) 
        cv2.putText(frame, 'If your game is visible then continue by clicking on the "Continue" button.', (round(height_current_text), round(height_current_text*4)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA)
        cv2.putText(frame, 'If your game is not visible, then disable full screen in your game settings.', (round(height_current_text), round(height_current_text*6)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA) 
        

        button_continue = 0.65, 0 + round(height_title_text*8)/frame_height, 0.75, 0 + 0.1 + round(height_title_text*8)/frame_height, 0.65, 0.06 + round(height_title_text*8)/frame_height, 0.8
        if mouseposx >= button_continue[0] and mouseposy >= button_continue[1] and mouseposx <= button_continue[2] and mouseposy <= button_continue[3]:
            cv2.rectangle(frame, (round(button_continue[0]*frame_width), round(button_continue[1]*frame_height)), (round(button_continue[2]*frame_width), round(button_continue[3]*frame_height)), green_hover, -1)
            if left_clicked == True:
                allow_detection = True
        else:
            cv2.rectangle(frame, (round(button_continue[0]*frame_width), round(button_continue[1]*frame_height)), (round(button_continue[2]*frame_width), round(button_continue[3]*frame_height)), green_normal, -1)
        current_text = "Continue"
        width_target_current_text = (button_continue[2]*frame_width - button_continue[0]*frame_width) * button_continue[6]
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
        cv2.putText(frame, "Continue", (round(button_continue[4]*frame_width+(button_continue[2]*frame_width-button_continue[0]*frame_width)/2-width_current_text/2), round(button_continue[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)


        button_exit = 0.25, 0 + round(height_title_text*8)/frame_height, 0.35, 0 + 0.1 + round(height_title_text*8)/frame_height, 0.25, 0.065 + round(height_title_text*8)/frame_height, 0.5
        if mouseposx >= button_exit[0] and mouseposy >= button_exit[1] and mouseposx <= button_exit[2] and mouseposy <= button_exit[3]:
            cv2.rectangle(frame, (round(button_exit[0]*frame_width), round(button_exit[1]*frame_height)), (round(button_exit[2]*frame_width), round(button_exit[3]*frame_height)), red_hover, -1)
            if left_clicked == True:
                break
        else:
            cv2.rectangle(frame, (round(button_exit[0]*frame_width), round(button_exit[1]*frame_height)), (round(button_exit[2]*frame_width), round(button_exit[3]*frame_height)), red_normal, -1)
        current_text = "Exit"
        width_target_current_text = (button_exit[2]*frame_width - button_exit[0]*frame_width) * button_exit[6]
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
        cv2.putText(frame, "Exit", (round(button_exit[4]*frame_width+(button_exit[2]*frame_width-button_exit[0]*frame_width)/2-width_current_text/2), round(button_exit[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)


        button_new_screenshot = 0.40, 0 + round(height_title_text*8)/frame_height, 0.60, 0 + 0.1 + round(height_title_text*8)/frame_height, 0.40, 0.065 + round(height_title_text*8)/frame_height, 0.9
        if mouseposx >= button_new_screenshot[0] and mouseposy >= button_new_screenshot[1] and mouseposx <= button_new_screenshot[2] and mouseposy <= button_new_screenshot[3]:
            cv2.rectangle(frame, (round(button_new_screenshot[0]*frame_width), round(button_new_screenshot[1]*frame_height)), (round(button_new_screenshot[2]*frame_width), round(button_new_screenshot[3]*frame_height)), blue_hover, -1)
            if left_clicked == True:
                screenshot = pyautogui.screenshot()
                game_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                game_frame_width = setupframe.shape[1]
                game_frame_height = setupframe.shape[0]
        else:
            cv2.rectangle(frame, (round(button_new_screenshot[0]*frame_width), round(button_new_screenshot[1]*frame_height)), (round(button_new_screenshot[2]*frame_width), round(button_new_screenshot[3]*frame_height)), blue_normal, -1)
        current_text = "New Screenshot"
        width_target_current_text = (button_new_screenshot[2]*frame_width - button_new_screenshot[0]*frame_width) * button_new_screenshot[6]
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
        cv2.putText(frame, "New Screenshot", (round(button_new_screenshot[4]*frame_width+(button_new_screenshot[2]*frame_width-button_new_screenshot[0]*frame_width)/2-width_current_text/2), round(button_new_screenshot[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)

        
        half_height = round(frame_height // 3)
        frame[half_height:, :] = game_frame[half_height:, :]

    else:

        if len(coordinates) < confirmation_count:
            screenshot = pyautogui.screenshot()
            game_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            game_frame_width = setupframe.shape[1]
            game_frame_height = setupframe.shape[0]

            frame = game_frame.copy()
            
            x1, y1, width, height = cv2.getWindowImageRect('Setup')
            cv2.rectangle(frame, (round(x1), round(y1)), (round(x1+width), round(y1+height)), (0, 0, 0), -1)

            current_text = 'Searching for a minimap and collecting data... This could take a few seconds...'
            width_target_current_text = 0.95*frame_width
            max_height_current_text = 0.027*frame_height
            fontscale_current_text = 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text = 3
            while width_current_text != width_target_current_text or height_current_text > max_height_current_text:
                fontscale_current_text *= min(width_target_current_text / width_current_text, max_height_current_text / height_current_text)
                textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                width_current_text, height_current_text = textsize_current_text
                max_count_current_text -= 1
                if max_count_current_text <= 0:
                    break
            width_title_text, height_title_text = textsize_current_text
            thickness_current_text = round(fontscale_current_text * 2)
            if thickness_current_text <= 0:
                thickness_current_text = 1
            cv2.rectangle(frame, (0, 0), (round(frame_width), round(height_title_text*7)), (0, 0, 0), -1)
            cv2.putText(frame, current_text, (round(height_current_text), round(height_current_text*2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA) 
            cv2.putText(frame, 'It could happen that this window will be unresponsive.', (round(height_current_text), round(height_current_text*4)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA) 
            cv2.putText(frame, f'({len(coordinates)+1} of {confirmation_count}, {round(100*(len(coordinates))/(confirmation_count-1))}%)', (round(height_current_text), round(height_current_text*6)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA) 
            
            results = model(frame)

            boxes = results.pandas().xyxy[0]

            found_map = False
            found_arrow = False
            map_coords = None
            arrow_coords = None
            max_map_score = 0
            max_arrow_score = 0

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
                x, y, x_max, y_max = map_coords
                cv2.rectangle(frame, (x, y), (x_max, y_max), (0, 255, 255), 2)
                cv2.putText(frame, f"{max_map_score:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 2, cv2.LINE_AA)

            if arrow_coords is not None:
                found_arrow = True
                x, y, x_max, y_max = arrow_coords
                cv2.rectangle(frame, (x, y), (x_max, y_max), (255, 0, 0), 2)
                cv2.putText(frame, f"{max_arrow_score:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 2, cv2.LINE_AA)
            
            if found_arrow == True and found_map == True:
                if map_coords[0] < arrow_coords[0] and map_coords[2] > arrow_coords[2] and map_coords[1] < arrow_coords[1] and map_coords[3] > arrow_coords[3]:
                    coordinates.append((map_coords[0], map_coords[1], map_coords[2], map_coords[3], arrow_coords[0], arrow_coords[1], arrow_coords[2], arrow_coords[3]))
        
        else:

            frame = setupframe.copy()
            
            
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
           
            cv2.rectangle(game_frame, (map_x1, map_y1), (map_x2, map_y2), (0, 255, 255), 2)
            cv2.putText(game_frame, f"Map", (map_x1, map_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 2, cv2.LINE_AA)
            
            cv2.rectangle(game_frame, (arrow_x1, arrow_y1), (arrow_x2, arrow_y2), (255, 0, 0), 2)
            cv2.putText(game_frame, f"Arrow", (arrow_x1, arrow_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 2, cv2.LINE_AA)
            
            x1 = round(map_x1-(map_x2-map_x1)*0.2)
            if x1 < 0:
                x1 = 0
            elif x1 > frame_width:
                x1 = frame_width
            x2 = round(map_x2+(map_x2-map_x1)*0.2)
            if x2 < 0:
                x2 = 0
            elif x2 > frame_width:
                x2 = frame_width
            y1 = round(map_y1-(map_y2-map_y1)*0.3)
            if y1 < 0:
                y1 = 0
            elif y1 > frame_height:
                y1 = frame_height
            y2 =round( map_y2+(map_y2-map_y1)*0.2)
            if y2 < 0:
                y2 = 0
            elif y2 > frame_height:
                y2 = frame_height

            resultsframe = game_frame[y1:y2, x1:x2]
            results_frame_width = resultsframe.shape[1]
            results_frame_height = resultsframe.shape[0]

            aspect_ratio = results_frame_width / results_frame_height
            new_height = int(0.7 * frame_height)
            new_width = int(aspect_ratio * new_height)
            resized_resultsframe = cv2.resize(resultsframe, (new_width, new_height))
            start_x = (frame_width - new_width) // 2
            start_y = frame_height - new_height
            frame[start_y:start_y+new_height, start_x:start_x+new_width] = resized_resultsframe


            current_text = 'Found the map and arrow position! Are the bounding boxes precise enough?'
            width_target_current_text = 0.95*frame_width
            max_height_current_text = 0.028*frame_height
            fontscale_current_text = 1
            textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
            width_current_text, height_current_text = textsize_current_text
            max_count_current_text = 3
            while width_current_text != width_target_current_text or height_current_text > max_height_current_text:
                fontscale_current_text *= min(width_target_current_text / width_current_text, max_height_current_text / height_current_text)
                textsize_current_text, _ = cv2.getTextSize(current_text, cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, 1)
                width_current_text, height_current_text = textsize_current_text
                max_count_current_text -= 1
                if max_count_current_text <= 0:
                    break
            width_title_text, height_title_text = textsize_current_text
            thickness_current_text = round(fontscale_current_text * 2)
            if thickness_current_text <= 0:
                thickness_current_text = 1
            cv2.rectangle(frame, (0, 0), (round(frame_width), round(height_current_text*7)), (0, 0, 0), -1)
            cv2.putText(frame, current_text, (round(height_current_text), round(height_current_text*2)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), thickness_current_text, cv2.LINE_AA) 
            

            button_finish = 0.75, 0 + round(height_title_text*4)/frame_height, 0.95, 0 + 0.1 + round(height_title_text*4)/frame_height, 0.75, 0.06 + round(height_title_text*4)/frame_height, 0.8
            if mouseposx >= button_finish[0] and mouseposy >= button_finish[1] and mouseposx <= button_finish[2] and mouseposy <= button_finish[3]:
                cv2.rectangle(frame, (round(button_finish[0]*frame_width), round(button_finish[1]*frame_height)), (round(button_finish[2]*frame_width), round(button_finish[3]*frame_height)), green_hover, -1)
                if left_clicked == True:
                    
                    CreateSettings("bettercam", "x", map_x1)
                    CreateSettings("bettercam", "y", map_y1)
                    CreateSettings("bettercam", "width", map_x2 - map_x1)
                    CreateSettings("bettercam", "height", map_y2 - map_y1)
                    
                    screencap_display = GetSettings("bettercam", "display")
                    if screencap_display == None:
                        CreateSettings("bettercam", "display", 0)
                        screencap_display = 0
                    screencap_device = GetSettings("bettercam", "device")
                    if screencap_device == None:
                        CreateSettings("bettercam", "device", 0)
                        screencap_device = 0
                    
                    CreateSettings("NavigationDetection", "map_topleft", (map_x1, map_y1))
                    CreateSettings("NavigationDetection", "map_bottomright", (map_x2, map_y2))
                    CreateSettings("NavigationDetection", "arrow_topleft", (arrow_x1, arrow_y1))
                    CreateSettings("NavigationDetection", "arrow_bottomright", (arrow_x2, arrow_y2))

                    frame = game_frame[arrow_y1:arrow_y2, arrow_x1:arrow_x2]
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
                        cv2.destroyWindow('Setup')
                    except:
                        pass

                    break

            else:
                cv2.rectangle(frame, (round(button_finish[0]*frame_width), round(button_finish[1]*frame_height)), (round(button_finish[2]*frame_width), round(button_finish[3]*frame_height)), green_normal, -1)
            current_text = "Yes, save and exit"
            width_target_current_text = (button_finish[2]*frame_width - button_finish[0]*frame_width) * button_finish[6]
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
            cv2.putText(frame, "Yes, save and exit", (round(button_finish[4]*frame_width+(button_finish[2]*frame_width-button_finish[0]*frame_width)/2-width_current_text/2), round(button_finish[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)


            button_exit = 0.05, 0 + round(height_title_text*4)/frame_height, 0.25, 0 + 0.1 + round(height_title_text*4)/frame_height, 0.05, 0.06 + round(height_title_text*4)/frame_height, 0.8
            if mouseposx >= button_exit[0] and mouseposy >= button_exit[1] and mouseposx <= button_exit[2] and mouseposy <= button_exit[3]:
                cv2.rectangle(frame, (round(button_exit[0]*frame_width), round(button_exit[1]*frame_height)), (round(button_exit[2]*frame_width), round(button_exit[3]*frame_height)), red_hover, -1)
                if left_clicked == True:
                    break
            else:
                cv2.rectangle(frame, (round(button_exit[0]*frame_width), round(button_exit[1]*frame_height)), (round(button_exit[2]*frame_width), round(button_exit[3]*frame_height)), red_normal, -1)
            current_text = "No, exit and don't save"
            width_target_current_text = (button_exit[2]*frame_width - button_exit[0]*frame_width) * button_exit[6]
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
            cv2.putText(frame, "No, exit and don't save", (round(button_exit[4]*frame_width+(button_exit[2]*frame_width-button_exit[0]*frame_width)/2-width_current_text/2), round(button_exit[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)


            button_try_again = 0.35, 0 + round(height_title_text*4)/frame_height, 0.65, 0 + 0.1 + round(height_title_text*4)/frame_height, 0.35, 0.06 + round(height_title_text*4)/frame_height, 0.8
            if mouseposx >= button_try_again[0] and mouseposy >= button_try_again[1] and mouseposx <= button_try_again[2] and mouseposy <= button_try_again[3]:
                cv2.rectangle(frame, (round(button_try_again[0]*frame_width), round(button_try_again[1]*frame_height)), (round(button_try_again[2]*frame_width), round(button_try_again[3]*frame_height)), orange_hover, -1)
                if left_clicked == True:
                    setupframe = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
                    screenshot = pyautogui.screenshot()
                    game_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    game_frame_width = setupframe.shape[1]
                    game_frame_height = setupframe.shape[0]
                    allow_detection = False
                    confirmation_count = 12
                    coordinates = []
            else:
                cv2.rectangle(frame, (round(button_try_again[0]*frame_width), round(button_try_again[1]*frame_height)), (round(button_try_again[2]*frame_width), round(button_try_again[3]*frame_height)), orange_normal, -1)
            current_text = "No, try again and don't save"
            width_target_current_text = (button_try_again[2]*frame_width - button_try_again[0]*frame_width) * button_try_again[6]
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
            cv2.putText(frame, "No, try again and don't save", (round(button_try_again[4]*frame_width+(button_try_again[2]*frame_width-button_try_again[0]*frame_width)/2-width_current_text/2), round(button_try_again[5]*frame_height)), cv2.FONT_HERSHEY_SIMPLEX, fontscale_current_text, (255, 255, 255), fontthickness_current_text, cv2.LINE_AA)



    cv2.imshow('Setup', frame)
    cv2.waitKey(1)