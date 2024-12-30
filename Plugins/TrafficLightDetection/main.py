from ETS2LA.Plugin import *
from ETS2LA.UI import *


def GetTextSize(Text="NONE", TextWidth=100, MaxTextHeight=100):
    Fontscale = 1
    Textsize, _ = cv2.getTextSize(Text, cv2.FONT_HERSHEY_SIMPLEX, Fontscale, 1)
    WidthCurrentText, HeightCurrentText = Textsize
    MaxCountCurrentText = 3
    while WidthCurrentText != TextWidth or HeightCurrentText > MaxTextHeight:
        Fontscale *= min(TextWidth / Textsize[0], MaxTextHeight / Textsize[1])
        Textsize, _ = cv2.getTextSize(Text, cv2.FONT_HERSHEY_SIMPLEX, Fontscale, 1)
        MaxCountCurrentText -= 1
        if MaxCountCurrentText <= 0:
            break
    Thickness = round(Fontscale * 2)
    if Thickness <= 0:
        Thickness = 1
    return Text, Fontscale, Thickness, Textsize[0], Textsize[1]


def ClassifyImage(Image):
    if pytorch.Loaded(Identifier) == False:
        return True

    Image = np.array(Image, dtype=np.float32)
    if pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'Grayscale' or pytorch.MODELS[Identifier]["IMG_CHANNELS"] == 'Binarize':
        Image = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
    else:
        Image = cv2.cvtColor(Image, cv2.COLOR_BGR2RGB)
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
    Class = np.argmax(Output)
    return True if Class != 3 else False


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="TrafficLightDetection",
        version="1.0",
        description="In Development.",
        modules=["TruckSimAPI"],
    )

    author = Author(
        name="Glas42",
        url="https://github.com/Glas42",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 500


    def imports(self):
        global SCSTelemetry, SCSController, ScreenCapture, ShowImage, variables, settings, pytorch, np, keyboard, time, cv2

        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        from Modules.SDKController.main import SCSController
        import Modules.BetterShowImage.main as ShowImage
        import ETS2LA.Utils.settings as settings
        import ETS2LA.Handlers.pytorch as pytorch
        import ETS2LA.variables as variables
        import numpy as np
        import keyboard
        import time
        import cv2

        global LastScreenCaptureCheck

        global Identifier

        global TruckSimAPI

        LastScreenCaptureCheck = 0

        Identifier = pytorch.Initialize(Owner="Glas42", Model="TrafficLightDetectionAI", Folder="model", Self=self)
        pytorch.Load(Identifier)

        TruckSimAPI = SCSTelemetry()

        ScreenCapture.Initialize()
        ShowImage.Initialize(Name="TrafficLightDetection", TitleBarColor=(0, 0, 0))


    def run(self):
        CurrentTime = time.time()

        global LastScreenCaptureCheck

        global TruckSimAPI

        APIDATA = TruckSimAPI.update()
        Frame = ScreenCapture.Capture(ImageType="cropped")

        if pytorch.Loaded(Identifier) == False: time.sleep(0.1); return
        if type(Frame) == type(None): return

        FrameWidth = Frame.shape[1]
        FrameHeight = Frame.shape[0]
        if FrameWidth <= 0 or FrameHeight <= 0:
            return

        if LastScreenCaptureCheck + 0.5 < CurrentTime:
            X1, Y1, X2, Y2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
            ScreenX, ScreenY, _, _ = ScreenCapture.GetScreenDimensions(ScreenCapture.GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2))
            if ScreenCapture.MonitorX1 != X1 - ScreenX or ScreenCapture.MonitorY1 != Y1 - ScreenY or ScreenCapture.MonitorX2 != X2 - ScreenX or ScreenCapture.MonitorY2 != Y2 - ScreenY:
                ScreenIndex = ScreenCapture.GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2)
                if ScreenCapture.Display != ScreenIndex - 1:
                    if ScreenCapture.CaptureLibrary == "WindowsCapture":
                        ScreenCapture.StopWindowsCapture = True
                        while ScreenCapture.StopWindowsCapture == True:
                            time.sleep(0.01)
                    ScreenCapture.Initialize()
                ScreenCapture.MonitorX1, ScreenCapture.MonitorY1, ScreenCapture.MonitorX2, ScreenCapture.MonitorY2 = ScreenCapture.ValidateCaptureArea(ScreenIndex, X1 - ScreenX, Y1 - ScreenY, X2 - ScreenX, Y2 - ScreenY)
            LastScreenCaptureCheck = CurrentTime

        ShowImage.Show("TrafficLightDetection", Frame)