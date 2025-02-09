from ETS2LA.Plugin import *
from ETS2LA.UI import *


PURPLE = "\033[95m"
NORMAL = "\033[0m"


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


def ConvertToAngle(X, Y):
    WindowX = ScreenCapture.MonitorX1
    WindowY = ScreenCapture.MonitorY1
    WindowWidth = ScreenCapture.MonitorX2 - ScreenCapture.MonitorX1
    WindowHeight = ScreenCapture.MonitorY2 - ScreenCapture.MonitorY1
    if WindowX == 0 and WindowY == 0:
        return 0, 0
    HorizontalFOV = (4 / 3) * math.atan((math.tan(math.radians(FOV / 2)) * (WindowWidth / WindowHeight)) / 1.333) * (360 / math.pi)
    VerticalFOV = math.atan(math.tan(math.radians(HorizontalFOV / 2)) / (WindowWidth / WindowHeight)) * (360 / math.pi)
    AngleX = (X - WindowWidth / 2) * (HorizontalFOV / WindowWidth)
    AngleY = (WindowHeight / 2 - Y) * (VerticalFOV / WindowHeight)
    return AngleX, AngleY


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="TrafficLightDetection",
        version="1.0",
        description="In Development.",
        modules=["TruckSimAPI"],
        tags=["Traffic Lights"]
    )

    author = Author(
        name="Glas42",
        url="https://github.com/OleFranz",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 500


    def imports(self):
        global SCSTelemetry, SCSController, ScreenCapture, SendCrashReport, ShowImage, variables, settings, pytorch, np, traceback, keyboard, math, time, cv2

        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        from Modules.SDKController.main import SCSController
        from ETS2LA.Networking.cloud import SendCrashReport
        import Modules.BetterShowImage.main as ShowImage
        import ETS2LA.Handlers.pytorch as pytorch
        import ETS2LA.Utils.settings as settings
        import ETS2LA.variables as variables
        import numpy as np
        import traceback
        import keyboard
        import math
        import time
        import cv2

        global FOV
        FOV = self.globals.settings.FOV
        if FOV == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for TrafficLightDetection! The plugin will disable itself.{NORMAL}\n")
            self.notify("No FOV set, disabling TrafficLightDetection...")
            time.sleep(1)
            self.terminate()

        global TruckSimAPI
        global Identifier

        TruckSimAPI = SCSTelemetry()
        ScreenCapture.Initialize()
        ShowImage.Initialize(Name="TrafficLightDetection", TitleBarColor=(0, 0, 0))
        Identifier = pytorch.Initialize(Owner="OleFranz", Model="TrafficLightDetectionAI", Folder="model", Self=self)
        pytorch.Load(Identifier)

        global LowerRed, UpperRed
        global LowerGreen, UpperGreen
        global LowerYellow, UpperYellow
        LowerRed = np.array([0, 0, 200])
        UpperRed = np.array([110, 110, 255])
        LowerGreen = np.array([0, 200, 0])
        UpperGreen = np.array([230, 255, 150])
        LowerYellow = np.array([50, 170, 200])
        UpperYellow = np.array([170, 240, 255])

        global WidthHeightRatioOffset
        global MinimalBlobSize, BlobPercentage, BlobPercentageOffset
        WidthHeightRatioOffset = 0.2
        MinimalBlobSize = 8
        BlobPercentage = 0.785
        BlobPercentageOffset = 0.15

        global Detections
        global TrafficLights
        Detections = []
        TrafficLights = []


    def run(self):
        CurrentTime = time.time()

        global TruckSimAPI

        global Detections
        global TrafficLights

        APIDATA = TruckSimAPI.update()
        Frame = ScreenCapture.Capture(ImageType="cropped")

        ScreenCapture.TrackWindow(Name="Truck Simulator", Blacklist=["Discord"])

        if pytorch.Loaded(Identifier) == False: time.sleep(0.1); return
        if type(Frame) == type(None): return
        FullFrame = Frame.copy()

        FrameWidth = Frame.shape[1]
        FrameHeight = Frame.shape[0]
        if FrameWidth <= 0 or FrameHeight <= 0:
            return


        TruckX = APIDATA["truckPlacement"]["coordinateX"]
        TruckY = APIDATA["truckPlacement"]["coordinateY"]
        TruckZ = APIDATA["truckPlacement"]["coordinateZ"]
        TruckRotationY = APIDATA["truckPlacement"]["rotationY"]
        TruckRotationX = APIDATA["truckPlacement"]["rotationX"]

        CabinOffsetX = APIDATA["headPlacement"]["cabinOffsetX"] + APIDATA["configVector"]["cabinPositionX"]
        CabinOffsetY = APIDATA["headPlacement"]["cabinOffsetY"] + APIDATA["configVector"]["cabinPositionY"]
        CabinOffsetZ = APIDATA["headPlacement"]["cabinOffsetZ"] + APIDATA["configVector"]["cabinPositionZ"]
        CabinOffsetRotationY = APIDATA["headPlacement"]["cabinOffsetrotationY"]
        CabinOffsetRotationX = APIDATA["headPlacement"]["cabinOffsetrotationX"]

        HeadOffsetX = APIDATA["headPlacement"]["headOffsetX"] + APIDATA["configVector"]["headPositionX"] + CabinOffsetX
        HeadOffsetY = APIDATA["headPlacement"]["headOffsetY"] + APIDATA["configVector"]["headPositionY"] + CabinOffsetY
        HeadOffsetZ = APIDATA["headPlacement"]["headOffsetZ"] + APIDATA["configVector"]["headPositionZ"] + CabinOffsetZ
        HeadOffsetRotationY = APIDATA["headPlacement"]["headOffsetrotationY"]
        HeadOffsetRotationX = APIDATA["headPlacement"]["headOffsetrotationX"]

        TruckRotationDegreesX = TruckRotationX * 360
        if TruckRotationDegreesX < 0:
            TruckRotationDegreesX = 360 + TruckRotationDegreesX
        TruckRotationRadiansX = -math.radians(TruckRotationDegreesX)

        HeadRotationDegreesX = (TruckRotationX + CabinOffsetRotationX + HeadOffsetRotationX) * 360
        if HeadRotationDegreesX < 0:
            HeadRotationDegreesX = 360 + HeadRotationDegreesX

        HeadRotationDegreesY = (TruckRotationY + CabinOffsetRotationY + HeadOffsetRotationY) * 360
        if HeadRotationDegreesY > 180:
            HeadRotationDegreesY = HeadRotationDegreesY - 360

        PointX = HeadOffsetX
        PointY = HeadOffsetY
        PointZ = HeadOffsetZ
        HeadX = PointX * math.cos(TruckRotationRadiansX) - PointZ * math.sin(TruckRotationRadiansX) + TruckX
        HeadY = PointY * math.cos(math.radians(HeadRotationDegreesY)) - PointZ * math.sin(math.radians(HeadRotationDegreesY)) + TruckY
        HeadZ = PointX * math.sin(TruckRotationRadiansX) + PointZ * math.cos(TruckRotationRadiansX) + TruckZ


        LastDetections = Detections.copy()
        Detections = []

        RedPixelMask = cv2.inRange(Frame, LowerRed, UpperRed)
        GreenPixelMask = cv2.inRange(Frame, LowerGreen, UpperGreen)
        YellowPixelMask = cv2.inRange(Frame, LowerYellow, UpperYellow)

        PixelMask = cv2.bitwise_or(RedPixelMask, cv2.bitwise_or(GreenPixelMask, YellowPixelMask))
        FilteredFrameColor = cv2.bitwise_and(Frame, Frame, mask=PixelMask)
        FilteredFrameGrayscale = cv2.cvtColor(FilteredFrameColor, cv2.COLOR_BGR2GRAY)
        for Contour in cv2.findContours(FilteredFrameGrayscale, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            X, Y, W, H = cv2.boundingRect(Contour)
            if MinimalBlobSize < W and MinimalBlobSize < H:
                if W / H - 1 < WidthHeightRatioOffset and W / H - 1 > -WidthHeightRatioOffset:
                    RedPixelCount = cv2.countNonZero(RedPixelMask[Y:Y+H, X:X+W])
                    GreenPixelCount = cv2.countNonZero(GreenPixelMask[Y:Y+H, X:X+W])
                    YellowPixelCount = cv2.countNonZero(YellowPixelMask[Y:Y+H, X:X+W])
                    TotalPixelCount = W * H
                    RedPixelRatio = RedPixelCount / TotalPixelCount
                    GreenPixelRatio = GreenPixelCount / TotalPixelCount
                    YellowPixelRatio = YellowPixelCount / TotalPixelCount
                    if (GreenPixelRatio < BlobPercentage + BlobPercentageOffset and GreenPixelRatio > BlobPercentage - BlobPercentageOffset and RedPixelRatio < 0.1 and YellowPixelRatio < 0.1 or 
                        RedPixelRatio < BlobPercentage + BlobPercentageOffset and RedPixelRatio > BlobPercentage - BlobPercentageOffset and GreenPixelRatio < 0.1 and YellowPixelRatio < 0.1 or 
                        YellowPixelRatio < BlobPercentage + BlobPercentageOffset and YellowPixelRatio > BlobPercentage - BlobPercentageOffset and GreenPixelRatio < 0.1 and RedPixelRatio < 0.1):
                        if RedPixelRatio > GreenPixelRatio and RedPixelRatio > YellowPixelRatio:
                            ColorString = "Red"
                            Offset = Y + H * 2
                        elif YellowPixelRatio > RedPixelRatio and YellowPixelRatio > GreenPixelRatio:
                            ColorString = "Yellow"
                            Offset = Y + H * 0.5
                        elif GreenPixelRatio > RedPixelRatio and GreenPixelRatio > YellowPixelRatio:
                            ColorString = "Green"
                            Offset = Y - H
                        else:
                            ColorString = "Red"
                            Offset = Y + H * 2
                        PointMask = []
                        PointMask.append((round(X + W * 0.05), round(Y + H * 0.05), False))
                        PointMask.append((round(X + W * 0.5), round(Y + H * 0.2), True))
                        PointMask.append((round(X + W * 0.95), round(Y + H * 0.05), False))
                        PointMask.append((round(X + W * 0.3), round(Y + H * 0.6), True))
                        PointMask.append((round(X + W * 0.5), round(Y + H * 0.5), True))
                        PointMask.append((round(X + W * 0.7), round(Y + H * 0.6), True))
                        PointMask.append((round(X + W * 0.05), round(Y + H * 0.95), False))
                        PointMask.append((round(X + W * 0.5), round(Y + H * 0.8), True))
                        PointMask.append((round(X + W * 0.95), round(Y + H * 0.95), False))
                        PointMaskAsExpected = True
                        for i in range(len(PointMask)):
                            PointX, PointY, ExpectedValue = PointMask[i]
                            Color = FilteredFrameGrayscale[PointY, PointX]
                            Color = True if Color != 0 else False
                            if Color != 0 == ExpectedValue:
                                PointMaskAsExpected = False
                                break
                        if PointMaskAsExpected:
                            Detections.append((round(X + W * 0.5), round(Offset), W, H, ColorString))


        try:
            if LastDetections:
                for i in range(len(LastDetections)):
                    LastX, LastY, W, H, State = LastDetections[i]
                    Closest = FullFrame.shape[1]
                    NearestPoint = None
                    ExistsInTrafficLights = False
                    SavedPosition = None
                    SavedID = None
                    SavedApproved = None
                    for j in range(len(Detections)):
                        X, Y, W, H, State = Detections[j]
                        Distance = math.sqrt((X - LastX)**2 + (Y - LastY)**2)
                        if Distance < Closest:
                            Closest = Distance
                            NearestPoint = X, Y, W, H, State

                    if NearestPoint:
                        for k, (Coordinate, Position, ID, Approved) in enumerate(TrafficLights):
                            if Coordinate == LastDetections[i]:
                                ExistsInTrafficLights = True
                                Angle = ConvertToAngle(NearestPoint[0], NearestPoint[1])[0]
                                SavedPosition = (Position[0], (HeadX, HeadZ, Angle, HeadRotationDegreesX), Position[2])
                                SavedID = ID
                                SavedApproved = Approved
                                del TrafficLights[k]
                                break
                        if ExistsInTrafficLights:
                            TrafficLights.append((NearestPoint, SavedPosition, SavedID, SavedApproved))
                        else:
                            UsedIDs = set(ID for _, _, ID, _ in TrafficLights)
                            NewID = 1
                            while NewID in UsedIDs:
                                NewID += 1

                            Angle = ConvertToAngle(NearestPoint[0], NearestPoint[1])[0]

                            X, Y, W, H, State = NearestPoint
                            Y1Classification = round(Y-H*4)
                            if Y1Classification < 0:
                                Y1Classification = 0
                            elif Y1Classification > FullFrame.shape[0]:
                                Y1Classification = FullFrame.shape[0]
                            Y2Classification = round(Y+H*4)
                            if Y2Classification < 0:
                                Y2Classification = 0
                            elif Y2Classification > FullFrame.shape[0]:
                                Y2Classification = FullFrame.shape[0]
                            X1Classification = round(X-W*2.5)
                            if X1Classification < 0:
                                X1Classification = 0
                            elif X1Classification > FullFrame.shape[1]:
                                X1Classification = FullFrame.shape[1]
                            X2Classification = round(X+W*2.5)
                            if X2Classification < 0:
                                X2Classification = 0
                            elif X2Classification > FullFrame.shape[1]:
                                X2Classification = FullFrame.shape[1]
                            Approved = ClassifyImage(FullFrame[Y1Classification:Y2Classification, X1Classification:X2Classification])

                            TrafficLights.append((NearestPoint, ((None, None, None), (HeadX, HeadZ, Angle, HeadRotationDegreesX), (HeadX, HeadZ, Angle, HeadRotationDegreesX)), NewID, Approved))

            Exists = []
            for CoordinateX, CoordinateY, _, _, _ in Detections:
                for (X, Y, _, _, _), _, ID, _ in TrafficLights:
                    if X == CoordinateX and Y == CoordinateY:
                        Exists.append(ID)
                        break
            for i, (_, _, ID, _) in enumerate(TrafficLights):
                if ID not in Exists:
                    del TrafficLights[i]
        except:
            EXC = traceback.format_exc()
            SendCrashReport("TrafficLightDetection - Tracking/AI Error.", str(EXC))
            print("TrafficLightDetection - Tracking/AI Error: " + str(EXC))


        try:
            for i in range(len(TrafficLights)):
                Coordinate, Position, ID, Approved = TrafficLights[i]
                X, Y, W, H, State = Coordinate
                Radius = round((W + H) / 4)
                Thickness = round((W + H) / 30)
                if Thickness < 1:
                    Thickness = 1
                if Approved == True:
                    if State == "Red":
                        Color = (0, 0, 255)
                    elif State == "Yellow":
                        Color = (0, 255, 255)
                    elif State == "Green":
                        Color = (0, 255, 0)
                    cv2.rectangle(Frame, (round(X - W * 1.1), round(Y - H * 2.5)), (round(X + W * 1.1), round(Y + H * 2.5)), Color, Radius)
                    cv2.rectangle(Frame, (round(X - W * 0.5), round(Y - H * 2)), (round(X + W * 0.5), round(Y - H)), (150, 150, 150), Thickness)
                    cv2.rectangle(Frame, (round(X - W * 0.5), round(Y - H * 0.5)), (round(X + W * 0.5), round(Y + H * 0.5)), (150, 150, 150), Thickness)
                    cv2.rectangle(Frame, (round(X + W * 0.5), round(Y + H * 2)), (round(X - W * 0.5), round(Y + H)), (150, 150, 150), Thickness)
        except Exception as e:
            EXC = traceback.format_exc()
            SendCrashReport("TrafficLightDetection - Draw Output Error.", str(EXC))
            print("TrafficLightDetection - Draw Output Error: " + str(EXC))


        ShowImage.Show("TrafficLightDetection", Frame)