from ETS2LA.Plugin import *
from ETS2LA.UI import *


PURPLE = "\033[95m"
NORMAL = "\033[0m"


def ConvertToScreenCoordinate(X: float, Y: float, Z: float):
    HeadYaw = HeadRotationDegreesX
    HeadPitch = HeadRotationDegreesY
    HeadRoll = HeadRotationDegreesZ

    RelativeX = X - HeadX
    RelativeY = Y - HeadY
    RelativeZ = Z - HeadZ

    CosYaw = math.cos(math.radians(-HeadYaw))
    SinYaw = math.sin(math.radians(-HeadYaw))
    NewX = RelativeX * CosYaw + RelativeZ * SinYaw
    NewZ = RelativeZ * CosYaw - RelativeX * SinYaw

    CosPitch = math.cos(math.radians(-HeadPitch))
    SinPitch = math.sin(math.radians(-HeadPitch))
    NewY = RelativeY * CosPitch - NewZ * SinPitch
    FinalZ = NewZ * CosPitch + RelativeY * SinPitch

    CosRoll = math.cos(math.radians(HeadRoll))
    SinRoll = math.sin(math.radians(HeadRoll))
    FinalX = NewX * CosRoll - NewY * SinRoll
    FinalY = NewY * CosRoll + NewX * SinRoll

    if FinalZ >= 0:
        return None, None, None

    FovRad = math.radians(FOV)
    
    WindowDistance = ((ScreenCapture.MonitorY2 - ScreenCapture.MonitorY1) * (4 / 3) / 2) / math.tan(FovRad / 2)

    ScreenX = (FinalX / FinalZ) * WindowDistance + (ScreenCapture.MonitorX2 - ScreenCapture.MonitorX1) / 2
    ScreenY = (FinalY / FinalZ) * WindowDistance + (ScreenCapture.MonitorY2 - ScreenCapture.MonitorY1) / 2

    ScreenX = (ScreenCapture.MonitorX2 - ScreenCapture.MonitorX1) - ScreenX

    Distance = math.sqrt((RelativeX ** 2) + (RelativeY ** 2) + (RelativeZ ** 2))

    return ScreenX, ScreenY, Distance


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="End-To-End",
        version="1.0",
        description="End-To-End works by following the current lane using a ML model which generates a steering value from the image.",
        modules=["TruckSimAPI", "SDKController"],
    )

    author = Author(
        name="Glas42",
        url="https://github.com/Glas42",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 500

    def imports(self):
        global SCSTelemetry, SCSController, ScreenCapture, ShowImage, variables, settings, pytorch, np, keyboard, math, time, cv2

        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        from Modules.SDKController.main import SCSController
        import Modules.BetterShowImage.main as ShowImage
        import ETS2LA.Utils.settings as settings
        import ETS2LA.Handlers.pytorch as pytorch
        import ETS2LA.variables as variables
        import numpy as np
        import keyboard
        import math
        import time
        import cv2

        global FOV
        global Enabled
        global EnableKey
        global EnableKeyPressed
        global LastEnableKeyPressed
        global LastScreenCaptureCheck
        global SteeringHistory

        global Identifier

        global SDKController
        global TruckSimAPI

        FOV = self.globals.settings.FOV
        if FOV == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for End-To-End! The plugin will disable itself.{NORMAL}\n")
            self.terminate()
        Enabled = True
        EnableKey = settings.Get("Steering", "EnableKey", "n")
        EnableKeyPressed = False
        LastEnableKeyPressed = False
        LastScreenCaptureCheck = 0
        SteeringHistory = []

        Identifier = pytorch.Initialize(Owner="Glas42", Model="End-To-End", Folder="model", Self=self)
        pytorch.Load(Identifier)

        SDKController = SCSController()
        TruckSimAPI = SCSTelemetry()

        ScreenCapture.Initialize()
        ShowImage.Initialize(Name="End-To-End", TitleBarColor=(0, 0, 0))

    def run(self):
        CurrentTime = time.time()

        global Enabled
        global EnableKey
        global EnableKeyPressed
        global LastEnableKeyPressed
        global LastScreenCaptureCheck

        global SDKController
        global TruckSimAPI

        global HeadRotationDegreesX
        global HeadRotationDegreesY
        global HeadRotationDegreesZ
        global HeadX
        global HeadY
        global HeadZ

        APIDATA = TruckSimAPI.update()

        if pytorch.Loaded(Identifier) == False: time.sleep(0.1); return

        if LastScreenCaptureCheck + 0.5 < time.time():
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

        Frame = ScreenCapture.Capture(ImageType="cropped")
        if type(Frame) == type(None) or Frame.shape[0] <= 0 or Frame.shape[1] <= 0:
            return


        TruckX = APIDATA["truckPlacement"]["coordinateX"]
        TruckY = APIDATA["truckPlacement"]["coordinateY"]
        TruckZ = APIDATA["truckPlacement"]["coordinateZ"]
        TruckRotationX = APIDATA["truckPlacement"]["rotationX"]
        TruckRotationY = APIDATA["truckPlacement"]["rotationY"]
        TruckRotationZ = APIDATA["truckPlacement"]["rotationZ"]

        CabinOffsetX = APIDATA["headPlacement"]["cabinOffsetX"] + APIDATA["configVector"]["cabinPositionX"]
        CabinOffsetY = APIDATA["headPlacement"]["cabinOffsetY"] + APIDATA["configVector"]["cabinPositionY"]
        CabinOffsetZ = APIDATA["headPlacement"]["cabinOffsetZ"] + APIDATA["configVector"]["cabinPositionZ"]
        CabinOffsetRotationX = APIDATA["headPlacement"]["cabinOffsetrotationX"]
        CabinOffsetRotationY = APIDATA["headPlacement"]["cabinOffsetrotationY"]
        CabinOffsetRotationZ = APIDATA["headPlacement"]["cabinOffsetrotationZ"]

        HeadOffsetX = APIDATA["headPlacement"]["headOffsetX"] + APIDATA["configVector"]["headPositionX"] + CabinOffsetX
        HeadOffsetY = APIDATA["headPlacement"]["headOffsetY"] + APIDATA["configVector"]["headPositionY"] + CabinOffsetY
        HeadOffsetZ = APIDATA["headPlacement"]["headOffsetZ"] + APIDATA["configVector"]["headPositionZ"] + CabinOffsetZ
        HeadOffsetRotationX = APIDATA["headPlacement"]["headOffsetrotationX"]
        HeadOffsetRotationY = APIDATA["headPlacement"]["headOffsetrotationY"]
        HeadOffsetRotationZ = APIDATA["headPlacement"]["headOffsetrotationZ"]

        TruckRotationDegreesX = TruckRotationX * 360
        TruckRotationRadiansX = -math.radians(TruckRotationDegreesX)

        HeadRotationDegreesX = (TruckRotationX + CabinOffsetRotationX + HeadOffsetRotationX) * 360
        while HeadRotationDegreesX > 360:
            HeadRotationDegreesX = HeadRotationDegreesX - 360

        HeadRotationDegreesY = (TruckRotationY + CabinOffsetRotationY + HeadOffsetRotationY) * 360

        HeadRotationDegreesZ = (TruckRotationZ + CabinOffsetRotationZ + HeadOffsetRotationZ) * 360

        PointX = HeadOffsetX
        PointY = HeadOffsetY
        PointZ = HeadOffsetZ
        HeadX = PointX * math.cos(TruckRotationRadiansX) - PointZ * math.sin(TruckRotationRadiansX) + TruckX
        HeadY = PointY + TruckY
        HeadZ = PointX * math.sin(TruckRotationRadiansX) + PointZ * math.cos(TruckRotationRadiansX) + TruckZ


        TruckWheelPointsX = [Point for Point in APIDATA["configVector"]["truckWheelPositionX"] if Point != 0]
        TruckWheelPointsY = [Point for Point in APIDATA["configVector"]["truckWheelPositionY"] if Point != 0]
        TruckWheelPointsZ = [Point for Point in APIDATA["configVector"]["truckWheelPositionZ"] if Point != 0]

        WheelAngles = [Angle for Angle in APIDATA["truckFloat"]["truck_wheelSteering"] if Angle != 0]
        while int(APIDATA["configUI"]["truckWheelCount"]) > len(WheelAngles):
            WheelAngles.append(0)

        for i in range(len(TruckWheelPointsX)):
            PointX = TruckX + TruckWheelPointsX[i] * math.cos(TruckRotationRadiansX) - TruckWheelPointsZ[i] * math.sin(TruckRotationRadiansX)
            PointY = TruckY + TruckWheelPointsY[i]
            PointZ = TruckZ + TruckWheelPointsZ[i] * math.cos(TruckRotationRadiansX) + TruckWheelPointsX[i] * math.sin(TruckRotationRadiansX)
            X, Y, D = ConvertToScreenCoordinate(X=PointX, Y=PointY, Z=PointZ)


        AllCoordinatesValid = True
        Points = []


        OffsetX = 2
        OffsetY = 0.1
        OffsetZ = 1.5

        PointX = HeadX + OffsetX * math.sin(TruckRotationRadiansX) - OffsetZ * math.cos(TruckRotationRadiansX)
        PointY = HeadY + OffsetY + math.tan(math.radians(TruckRotationY * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
        PointZ = HeadZ - OffsetX * math.cos(TruckRotationRadiansX) - OffsetZ * math.sin(TruckRotationRadiansX)

        X, Y, D = ConvertToScreenCoordinate(PointX, PointY, PointZ)
        if X == None or Y == None:
            AllCoordinatesValid = False
        else:
            TopLeft = X, Y
            Points.append((PointX, PointY, PointZ))


        OffsetX = 2
        OffsetY = 0.1
        OffsetZ = -1.5

        PointX = HeadX + OffsetX * math.sin(TruckRotationRadiansX) - OffsetZ * math.cos(TruckRotationRadiansX)
        PointY = HeadY + OffsetY + math.tan(math.radians(TruckRotationY * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
        PointZ = HeadZ - OffsetX * math.cos(TruckRotationRadiansX) - OffsetZ * math.sin(TruckRotationRadiansX)

        X, Y, D = ConvertToScreenCoordinate(PointX, PointY, PointZ)
        if X == None or Y == None:
            AllCoordinatesValid = False
        else:
            TopRight = X, Y
            Points.append((PointX, PointY, PointZ))


        OffsetX = 2
        OffsetY = -0.5
        OffsetZ = 1.5

        PointX = HeadX + OffsetX * math.sin(TruckRotationRadiansX) - OffsetZ * math.cos(TruckRotationRadiansX)
        PointY = HeadY + OffsetY + math.tan(math.radians(TruckRotationY * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
        PointZ = HeadZ - OffsetX * math.cos(TruckRotationRadiansX) - OffsetZ * math.sin(TruckRotationRadiansX)

        X, Y, D = ConvertToScreenCoordinate(PointX, PointY, PointZ)
        if X == None or Y == None:
            AllCoordinatesValid = False
        else:
            BottomLeft = X, Y
            Points.append((PointX, PointY, PointZ))


        OffsetX = 2
        OffsetY = -0.5
        OffsetZ = -1.5

        PointX = HeadX + OffsetX * math.sin(TruckRotationRadiansX) - OffsetZ * math.cos(TruckRotationRadiansX)
        PointY = HeadY + OffsetY + math.tan(math.radians(TruckRotationY * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
        PointZ = HeadZ - OffsetX * math.cos(TruckRotationRadiansX) - OffsetZ * math.sin(TruckRotationRadiansX)

        X, Y, D = ConvertToScreenCoordinate(PointX, PointY, PointZ)
        if X == None or Y == None:
            AllCoordinatesValid = False
        else:
            BottomRight = X, Y
            Points.append((PointX, PointY, PointZ))


        if AllCoordinatesValid:
            try:
                CroppedWidth = round(max(TopRight[0] - TopLeft[0], BottomRight[0] - BottomLeft[0]))
                CroppedHeight = round(max(BottomLeft[1] - TopLeft[1], BottomRight[1] - TopRight[1]))
                SourcePoints = np.float32([TopLeft, TopRight, BottomLeft, BottomRight])
                DestinationPoints = np.float32([[0, 0], [CroppedWidth, 0], [0, CroppedHeight], [CroppedWidth, CroppedHeight]])
                Matrix = cv2.getPerspectiveTransform(SourcePoints, DestinationPoints)
                Frame = cv2.warpPerspective(Frame, Matrix, (CroppedWidth, CroppedHeight))
            except:
                # It sometimes happens that it tries to generate a frames which needs gigabytes of memory which will result in a crash, we can just ignore it.
                pass


        Image = np.array(Frame, dtype=np.float32)
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


        EnableKeyPressed = keyboard.is_pressed(EnableKey)
        if EnableKeyPressed == False and LastEnableKeyPressed == True:
            Enabled = not Enabled
        LastEnableKeyPressed = EnableKeyPressed

        Output = [[0] * pytorch.MODELS[Identifier]["OUTPUTS"]]

        if Enabled == True:
            if pytorch.MODELS[Identifier]["ModelLoaded"] == True:
                with pytorch.torch.no_grad():
                    Output = pytorch.MODELS[Identifier]["Model"](Image)
                    Output = Output.tolist()

        Steering = float(Output[0][0]) / -20

        SteeringHistory.append((Steering, CurrentTime))
        SteeringHistory.sort(key=lambda x: x[1])
        while CurrentTime - SteeringHistory[0][1] > 0.2:
            SteeringHistory.pop(0)
        Steering = sum(x[0] for x in SteeringHistory) / len(SteeringHistory)

        SDKController.steering = Steering

        FrameWidth = Frame.shape[1]
        FrameHeight = Frame.shape[0]

        if Enabled == True:
            cv2.rectangle(Frame, (0, 0), (FrameWidth - 1, FrameHeight - 1), (0, 255, 0), 3)
        else:
            cv2.rectangle(Frame, (0, 0), (FrameWidth - 1, FrameHeight - 1), (0, 0, 255), 3)

        CurrentDesired = Steering
        ActualSteering = -APIDATA["truckFloat"]["gameSteer"]

        Divider = 5
        cv2.line(Frame, (int(FrameWidth/Divider), int(FrameHeight - FrameHeight/10)), (int(FrameWidth/Divider*(Divider-1)), int(FrameHeight - FrameHeight/10)), (100, 100, 100), 6, cv2.LINE_AA)
        cv2.line(Frame, (int(FrameWidth/2), int(FrameHeight - FrameHeight/10)), (int(FrameWidth/2 + ActualSteering * (FrameWidth/2 - FrameWidth/Divider)), int(FrameHeight - FrameHeight/10)), (0, 255, 100), 6, cv2.LINE_AA)
        cv2.line(Frame, (int(FrameWidth/2), int(FrameHeight - FrameHeight/10)), (int(FrameWidth/2 + (CurrentDesired if abs(CurrentDesired) < 1 else (1 if CurrentDesired > 0 else -1)) * (FrameWidth/2 - FrameWidth/Divider)), int(FrameHeight - FrameHeight/10)), (0, 100, 255), 2, cv2.LINE_AA)

        ShowImage.Show("End-To-End", Frame)