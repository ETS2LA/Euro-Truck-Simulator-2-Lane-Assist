import ETS2LA.Handlers.pytorch as pytorch
import ETS2LA.variables as variables
import numpy as np
import threading
import traceback
import math
import time
import cv2
import mss

if variables.OS == "nt":
    import win32gui


def SendCrashReport(Title, Description):
    print("NOT IMPLEMENTED: SendCrashReport")

sct = mss.mss()
if len(sct.monitors) < 2:
    SendCrashReport("ScreenCapture - Only one item in the monitor list, normally there should be at least two.", str(sct.monitors))
    Monitor = sct.monitors[0]
else:
    Monitor = sct.monitors[1]
ScreenX = Monitor["left"]
ScreenY = Monitor["top"]
ScreenWidth = Monitor["width"]
ScreenHeight = Monitor["height"]
LastWindowPositions = {}
LastForegroundWindows = {}
LastTrackWindowUpdates = {}
LastTrackWindowRouteAdvisorUpdates = {}


def Initialize(Screen=None, Area=(None, None, None, None)):
    global Display
    global Monitor
    global MonitorX1
    global MonitorY1
    global MonitorX2
    global MonitorY2
    global Cam
    global CaptureLibrary
    global RouteAdvisorSide
    global RouteAdvisorZoomCorrect
    global RouteAdvisorTabCorrect

    Display = Screen if Screen != None else 0
    Monitor = sct.monitors[(Display + 1)]
    MonitorX1 = Area[0] if Area[0] != None else Monitor["left"]
    MonitorY1 = Area[1] if Area[1] != None else Monitor["top"]
    MonitorX2 = Area[2] if Area[2] != None else Monitor["width"]
    MonitorY2 = Area[3] if Area[3] != None else Monitor["height"]
    Cam = None
    CaptureLibrary = None
    RouteAdvisorSide = "Right"
    RouteAdvisorZoomCorrect = True
    RouteAdvisorTabCorrect = True

    try:

        if variables.OS == "nt":

            try:

                from windows_capture import WindowsCapture, Frame, InternalCaptureControl
                Capture = WindowsCapture(
                    cursor_capture=False,
                    draw_border=False,
                    monitor_index=Display + 1,
                    window_name=None,
                )
                global WindowsCaptureFrame
                global StopWindowsCapture
                StopWindowsCapture = False
                @Capture.event
                def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
                    global WindowsCaptureFrame
                    global StopWindowsCapture
                    WindowsCaptureFrame = frame.convert_to_bgr().frame_buffer.copy()
                    if StopWindowsCapture:
                        StopWindowsCapture = False
                        capture_control.stop()
                @Capture.event
                def on_closed():
                    print("Capture Session Closed")
                try:
                    Control.stop()
                except:
                    pass
                Control = Capture.start_free_threaded()

                CaptureLibrary = "WindowsCapture"

            except:

                import bettercam
                try:
                    Cam.stop()
                except:
                    pass
                try:
                    Cam.close()
                except:
                    pass
                try:
                    Cam.release()
                except:
                    pass
                try:
                    del Cam
                except:
                    pass
                Cam = bettercam.create(output_idx=Display, output_color="BGR")
                Cam.start()
                Cam.get_latest_frame()
                CaptureLibrary = "BetterCam"

        else:

            CaptureLibrary = "MSS"

    except:

        CaptureLibrary = "MSS"


def Capture(ImageType:str = "both"):
    """ImageType: "both", "cropped", "full" """

    if CaptureLibrary.lower() == "windowscapture":

        try:

            img = cv2.cvtColor(np.array(WindowsCaptureFrame), cv2.COLOR_BGRA2BGR)
            if ImageType.lower() == "both":
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg, img
            elif ImageType.lower() == "cropped":
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg
            elif ImageType.lower() == "full":
                return img
            else:
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg, img

        except:

            return None if ImageType.lower() == "cropped" or ImageType.lower() == "full" else (None, None)

    elif CaptureLibrary.lower() == "bettercam":

        try:

            if Cam == None:
                Initialize()
            img = np.array(Cam.get_latest_frame())
            if ImageType.lower() == "both":
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg, img
            elif ImageType.lower() == "cropped":
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg
            elif ImageType.lower() == "full":
                return img
            else:
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg, img

        except:

            return None if ImageType.lower() == "cropped" or ImageType.lower() == "full" else (None, None)

    elif CaptureLibrary.lower() == "mss":

        try:

            fullMonitor = sct.monitors[(Display + 1)]
            img = np.array(sct.grab(fullMonitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            if ImageType.lower() == "both":
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg, img
            elif ImageType.lower() == "cropped":
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg
            elif ImageType.lower() == "full":
                return img
            else:
                croppedImg = img[MonitorY1:MonitorY2, MonitorX1:MonitorX2]
                return croppedImg, img

        except:

            return None if ImageType.lower() == "cropped" or ImageType.lower() == "full" else (None, None)


def GetScreenDimensions(Display=1):
    global ScreenX, ScreenY, ScreenWidth, ScreenHeight
    Monitor = sct.monitors[Display]
    ScreenX = Monitor["left"]
    ScreenY = Monitor["top"]
    ScreenWidth = Monitor["width"]
    ScreenHeight = Monitor["height"]
    return ScreenX, ScreenY, ScreenWidth, ScreenHeight


def GetScreenIndex(X, Y):
    Monitors = sct.monitors
    ClosestScreenIndex = None
    ClosestDistance = float('inf')
    for i, Monitor in enumerate(Monitors[1:]):
        CenterX = (Monitor['left'] + Monitor['left'] + Monitor['width']) // 2
        CenterY = (Monitor['top'] + Monitor['top'] + Monitor['height']) // 2
        Distance = ((CenterX - X) ** 2 + (CenterY - Y) ** 2) ** 0.5
        if Distance < ClosestDistance:
            ClosestScreenIndex = i + 1
            ClosestDistance = Distance
    return ClosestScreenIndex


def ValidateCaptureArea(Display, X1, Y1, X2, Y2):
    Monitor = sct.monitors[Display]
    Width, Height = Monitor["width"], Monitor["height"]
    X1 = max(0, min(Width - 1, X1))
    X2 = max(0, min(Width - 1, X2))
    Y1 = max(0, min(Height - 1, Y1))
    Y2 = max(0, min(Height - 1, Y2))
    if X1 == X2:
        if X1 == 0:
            X2 = Width - 1
        else:
            X1 = 0
    if Y1 == Y2:
        if Y1 == 0:
            Y2 = Height - 1
        else:
            Y1 = 0
    return X1, Y1, X2, Y2


def IsForegroundWindow(Name="", Blacklist=[""]):
    if variables.OS == "nt":
        Key = f"{Name}{Blacklist}"
        if Key not in LastForegroundWindows:
            LastForegroundWindows[Key] = [0, ScreenX, ScreenY, ScreenX + ScreenWidth, ScreenY + ScreenHeight]
        if LastForegroundWindows[Key][0] + 1 < time.time():
            HWND = None
            TopWindows = []
            IsForeground = LastForegroundWindows[Key][1]
            win32gui.EnumWindows(lambda HWND, TopWindows: TopWindows.append((HWND, win32gui.GetWindowText(HWND))), TopWindows)
            for HWND, WindowText in TopWindows:
                if Name in WindowText and all(BlacklistItem not in WindowText for BlacklistItem in Blacklist):
                    IsForeground = (HWND == win32gui.GetForegroundWindow())
                    break
            LastForegroundWindows[Key] = time.time(), IsForeground
            return IsForeground
        else:
            return LastForegroundWindows[Key][1]
    else:
        return True


def GetWindowPosition(Name="", Blacklist=[""]):
    global LastWindowPositions
    if variables.OS == "nt":
        Key = f"{Name}{Blacklist}"
        if Key not in LastWindowPositions:
            LastWindowPositions[Key] = [0, ScreenX, ScreenY, ScreenX + ScreenWidth, ScreenY + ScreenHeight]
        if LastWindowPositions[Key][0] + 1 < time.time():
            HWND = None
            TopWindows = []
            Window = LastWindowPositions[Key][1], LastWindowPositions[Key][2], LastWindowPositions[Key][3], LastWindowPositions[Key][4]
            win32gui.EnumWindows(lambda HWND, TopWindows: TopWindows.append((HWND, win32gui.GetWindowText(HWND))), TopWindows)
            for HWND, WindowText in TopWindows:
                if Name in WindowText and all(BlacklistItem not in WindowText for BlacklistItem in Blacklist):
                    RECT = win32gui.GetClientRect(HWND)
                    TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
                    BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
                    Window = (TopLeft[0], TopLeft[1], BottomRight[0] - TopLeft[0], BottomRight[1] - TopLeft[1])
                    break
            LastWindowPositions[Key] = time.time(), Window[0], Window[1], Window[0] + Window[2], Window[1] + Window[3]
            return Window[0], Window[1], Window[0] + Window[2], Window[1] + Window[3]
        else:
            return LastWindowPositions[Key][1], LastWindowPositions[Key][2], LastWindowPositions[Key][3], LastWindowPositions[Key][4]
    else:
        return ScreenX, ScreenY, ScreenX + ScreenWidth, ScreenY + ScreenHeight


def GetRouteAdvisorPosition(Name="", Blacklist=[""], Side="Automatic"):
    X1, Y1, X2, Y2 = GetWindowPosition(Name=Name, Blacklist=Blacklist)
    DistanceFromRight = 21
    DistanceFromBottom = 100
    Width = 420
    Height = 219
    Scale = (Y2 - Y1) / 1080

    if Side == "Automatic" and pytorch.TorchAvailable == False:
        Side = "Right"

    if Side == "Left" or Side == "Automatic":
        X = X1 + (DistanceFromRight * Scale) - 1
        Y = Y1 + (Y2 - Y1) - (DistanceFromBottom * Scale + Height * Scale)
        LeftMapTopLeft = (round(X), round(Y))
        X = X1 + (DistanceFromRight * Scale + Width * Scale) - 1
        Y = Y1 + (Y2 - Y1) - (DistanceFromBottom * Scale)
        LeftMapBottomRight = (round(X), round(Y))
        X = LeftMapBottomRight[0] - (LeftMapBottomRight[0] - LeftMapTopLeft[0]) * 0.57 - 1
        Y = LeftMapBottomRight[1] - (LeftMapBottomRight[1] - LeftMapTopLeft[1]) * 0.575
        LeftArrowTopLeft = (round(X), round(Y))
        X = LeftMapBottomRight[0] - (LeftMapBottomRight[0] - LeftMapTopLeft[0]) * 0.43 - 1
        Y = LeftMapBottomRight[1] - (LeftMapBottomRight[1] - LeftMapTopLeft[1]) * 0.39
        LeftArrowBottomRight = (round(X), round(Y))
        if Side == "Automatic":
            LeftImage = np.array(sct.grab({"left": LeftMapTopLeft[0], "top": LeftMapTopLeft[1], "width": LeftMapBottomRight[0] - LeftMapTopLeft[0], "height": LeftMapBottomRight[1] - LeftMapTopLeft[1]}), dtype=np.float32)

    if Side == "Right" or Side == "Automatic":
        X = X1 + (X2 - X1) - (DistanceFromRight * Scale + Width * Scale)
        Y = Y1 + (Y2 - Y1) - (DistanceFromBottom * Scale + Height * Scale)
        RightMapTopLeft = (round(X), round(Y))
        X = X1 + (X2 - X1) - (DistanceFromRight * Scale)
        Y = Y1 + (Y2 - Y1) - (DistanceFromBottom * Scale)
        RightMapBottomRight = (round(X), round(Y))
        X = RightMapBottomRight[0] - (RightMapBottomRight[0] - RightMapTopLeft[0]) * 0.57
        Y = RightMapBottomRight[1] - (RightMapBottomRight[1] - RightMapTopLeft[1]) * 0.575
        RightArrowTopLeft = (round(X), round(Y))
        X = RightMapBottomRight[0] - (RightMapBottomRight[0] - RightMapTopLeft[0]) * 0.43
        Y = RightMapBottomRight[1] - (RightMapBottomRight[1] - RightMapTopLeft[1]) * 0.39
        RightArrowBottomRight = (round(X), round(Y))
        if Side == "Automatic":
            RightImage = np.array(sct.grab({"left": RightMapTopLeft[0], "top": RightMapTopLeft[1], "width": RightMapBottomRight[0] - RightMapTopLeft[0], "height": RightMapBottomRight[1] - RightMapTopLeft[1]}), dtype=np.float32)

    if Side == "Automatic":
        global RouteAdvisorSide
        global RouteAdvisorZoomCorrect
        global RouteAdvisorTabCorrect

        if pytorch.IsInitialized(Model="RouteAdvisorClassification", Folder="model") == False:
            global Identifier
            Identifier = pytorch.Initialize(Owner="Glas42", Model="RouteAdvisorClassification", Folder="model")
            pytorch.Load(Identifier)
        if pytorch.Loaded(Identifier) == False:
            return RightMapTopLeft, RightMapBottomRight, RightArrowTopLeft, RightArrowBottomRight

        Outputs = []
        for Image in [LeftImage, RightImage]:
            if type(Image) == type(None):
                return RightMapTopLeft, RightMapBottomRight, RightArrowTopLeft, RightArrowBottomRight
            if Image.shape[1] <= 0 or Image.shape[0] <= 0:
                return RightMapTopLeft, RightMapBottomRight, RightArrowTopLeft, RightArrowBottomRight
            if pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'Grayscale' or pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'Binarize':
                Image = cv2.cvtColor(Image, cv2.COLOR_RGB2GRAY)
            if pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'RG':
                Image = np.stack((Image[:, :, 0], Image[:, :, 1]), axis=2)
            elif pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'GB':
                Image = np.stack((Image[:, :, 1], Image[:, :, 2]), axis=2)
            elif pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'RB':
                Image = np.stack((Image[:, :, 0], Image[:, :, 2]), axis=2)
            elif pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'R':
                Image = Image[:, :, 0]
                Image = np.expand_dims(Image, axis=2)
            elif pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'G':
                Image = Image[:, :, 1]
                Image = np.expand_dims(Image, axis=2)
            elif pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'B':
                Image = Image[:, :, 2]
                Image = np.expand_dims(Image, axis=2)
            Image = cv2.resize(Image, (pytorch.MODELS[Identifier]["IMG_WIDTH"], pytorch.MODELS[Identifier]["IMG_HEIGHT"]))
            Image = Image / 255.0
            if pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'Binarize':
                Image = cv2.threshold(Image, 0.5, 1.0, cv2.THRESH_BINARY)[1]

            Image = pytorch.transforms.ToTensor()(Image).unsqueeze(0).to(pytorch.MODELS[Identifier]["Device"])
            with pytorch.torch.no_grad():
                Output = np.array(pytorch.MODELS[Identifier]["Model"](Image)[0].tolist())
            Outputs.append(Output)

        RouteAdvisorSide = "Left" if Outputs[0][0] > Outputs[1][0] else "Right"
        RouteAdvisorZoomCorrect = Outputs[0 if RouteAdvisorSide == "Left" else 1][1] > 0.5
        RouteAdvisorTabCorrect = Outputs[0 if RouteAdvisorSide == "Left" else 1][2] > 0.5

        if RouteAdvisorSide == "Right":
            return RightMapTopLeft, RightMapBottomRight, RightArrowTopLeft, RightArrowBottomRight
        else:
            return LeftMapTopLeft, LeftMapBottomRight, LeftArrowTopLeft, LeftArrowBottomRight

    elif Side == "Left":
        return LeftMapTopLeft, LeftMapBottomRight, LeftArrowTopLeft, LeftArrowBottomRight
    elif Side == "Right":
        return RightMapTopLeft, RightMapBottomRight, RightArrowTopLeft, RightArrowBottomRight


def TrackWindow(Name="", Blacklist=[""], Rate=2):
    Key = f"{Name}{Blacklist}"
    if Key not in LastTrackWindowUpdates:
        LastTrackWindowUpdates[Key] = 0
    if Rate > 0:
        if LastTrackWindowUpdates[Key] + 1/Rate > time.time():
            return
    global StopWindowsCapture, MonitorX1, MonitorY1, MonitorX2, MonitorY2
    X1, Y1, X2, Y2 = GetWindowPosition(Name=Name, Blacklist=Blacklist)
    ScreenX, ScreenY, _, _ = GetScreenDimensions(GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2))
    if MonitorX1 != X1 - ScreenX or MonitorY1 != Y1 - ScreenY or MonitorX2 != X2 - ScreenX or MonitorY2 != Y2 - ScreenY:
        ScreenIndex = GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2)
        if Display != ScreenIndex - 1:
            if CaptureLibrary == "WindowsCapture":
                StopWindowsCapture = True
                while StopWindowsCapture == True:
                    time.sleep(0.01)
            Initialize()
        MonitorX1, MonitorY1, MonitorX2, MonitorY2 = ValidateCaptureArea(ScreenIndex, X1 - ScreenX, Y1 - ScreenY, X2 - ScreenX, Y2 - ScreenY)
    LastTrackWindowUpdates[Key] = time.time()


def TrackWindowRouteAdvisor(Name="", Blacklist=[""], Side="Automatic", Rate=2):
    Key = f"{Name}{Blacklist}{Side}"
    if Key not in LastTrackWindowRouteAdvisorUpdates:
        LastTrackWindowRouteAdvisorUpdates[Key] = 0
    if Rate > 0:
        if LastTrackWindowRouteAdvisorUpdates[Key] + 1/Rate > time.time():
            return
    global StopWindowsCapture, MonitorX1, MonitorY1, MonitorX2, MonitorY2
    MapTopLeft, MapBottomRight, ArrowTopLeft, ArrowBottomRight = GetRouteAdvisorPosition(Name=Name, Blacklist=Blacklist, Side=Side)
    ScreenX, ScreenY, _, _ = GetScreenDimensions(GetScreenIndex((MapTopLeft[0] + MapBottomRight[0]) / 2, (MapTopLeft[1] + MapBottomRight[1]) / 2))
    if MonitorX1 != MapTopLeft[0] - ScreenX or MonitorY1 != MapTopLeft[1] - ScreenY or MonitorX2 != MapBottomRight[0] - ScreenX or MonitorY2 != MapBottomRight[1] - ScreenY:
        ScreenIndex = GetScreenIndex((MapTopLeft[0] + MapBottomRight[0]) / 2, (MapTopLeft[1] + MapBottomRight[1]) / 2)
        if Display != ScreenIndex - 1:
            if CaptureLibrary == "WindowsCapture":
                StopWindowsCapture = True
                while StopWindowsCapture == True:
                    time.sleep(0.01)
            Initialize()
        MonitorX1, MonitorY1, MonitorX2, MonitorY2 = ValidateCaptureArea(ScreenIndex, MapTopLeft[0] - ScreenX, MapTopLeft[1] - ScreenY, MapBottomRight[0] - ScreenX, MapBottomRight[1] - ScreenY)
    LastTrackWindowRouteAdvisorUpdates[Key] = time.time()


def ConvertToAngle(X, Y):
    _, _, WindowWidth, WindowHeight = GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
    FOV_RADIANS = math.radians(variables.FOV)
    WindowDistance = (WindowHeight * (4 / 3) / 2) / math.tan(FOV_RADIANS / 2)
    AngleX = math.atan2(X - WindowWidth / 2, WindowDistance) * (180 / math.pi)
    AngleY = math.atan2(Y - WindowHeight / 2, WindowDistance) * (180 / math.pi)
    return AngleX, AngleY