from ETS2LA.Plugin import *
from ETS2LA.UI import *


from ETS2LA.Controls import ControlEvent
from ETS2LA.Events import *

EnableDisable = ControlEvent(
    "toggle_vision_adaptive_cruise_control",
    "Toggle",
    "button",
    description="When VACC is running this will toggle it on/off.",
    default="n"
)


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


def CalculateRadiusFrontWheel(SteeringAngle, Distance):
    SteeringAngle = math.radians(SteeringAngle)
    if SteeringAngle != 0:
        return Distance / math.sin(SteeringAngle)
    else:
        return float("inf")


def CalculateRadiusBackWheel(SteeringAngle, Distance):
    SteeringAngle = math.radians(SteeringAngle)
    if SteeringAngle != 0:
        return Distance / math.tan(SteeringAngle)
    else:
        return float("inf")


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="VisionAdaptiveCruiseControl",
        version="1.0",
        description="Adaptive Cruise Control using vision to determine the distance to the leading vehicle.",
        modules=["TruckSimAPI", "SDKController", "Camera"],
        tags=["Vision"]
    )

    author = Author(
        name="Glas42",
        url="https://github.com/OleFranz",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 500

    controls = [EnableDisable]

    global Enabled; Enabled = True
    @events.on("toggle_vision_adaptive_cruise_control")
    def on_toggle_vision_adaptive_cruise_control(self, state:bool):
        # WTF?? Why so complicated
        if not state: return
        global Enabled; Enabled = not Enabled

    def imports(self):
        global SCSTelemetry, SCSController, ScreenCapture, ShowImage, pytorch, variables, settings, np, math, time, cv2
        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        from Modules.SDKController.main import SCSController
        import Modules.BetterShowImage.main as ShowImage
        import ETS2LA.Handlers.pytorch as pytorch
        import ETS2LA.Utils.settings as settings
        import ETS2LA.variables as variables
        import numpy as np
        import math
        import time
        import cv2

        global Model

        global ValueHistory

        global SDKController
        global TruckSimAPI
        global FOV

        Model = pytorch.Model(HF_owner="OleFranz", HF_repository="AdaptiveCruiseControl", HF_model_folder="model", plugin_self=self)
        Model.load_model()

        ValueHistory = []

        SDKController = SCSController()
        TruckSimAPI = SCSTelemetry()

        FOV = self.globals.settings.FOV
        if FOV == 0:
            FOV = 80

        ScreenCapture.Initialize()
        ShowImage.Initialize(Name="AdaptiveCruiseControl", TitleBarColor=(0, 0, 0))

    def run(self):
        CurrentTime = time.time()

        global SDKController
        global TruckSimAPI

        global HeadRotationDegreesX
        global HeadRotationDegreesY
        global HeadRotationDegreesZ
        global HeadX
        global HeadY
        global HeadZ

        APIDATA = TruckSimAPI.update()

        if Model.loaded == False: time.sleep(0.1); return

        ScreenCapture.TrackWindow(Name="Truck Simulator", Blacklist=["Discord"])

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


        CameraData = self.modules.Camera.run()
        if CameraData is not None:
            FOV = CameraData.fov
            Angles = CameraData.rotation.euler()
            HeadX = CameraData.position.x + CameraData.cx * 512
            HeadY = CameraData.position.y
            HeadZ = CameraData.position.z + CameraData.cz * 512
            HeadRotationDegreesX = Angles[1]
            HeadRotationDegreesY = Angles[0]
            HeadRotationDegreesZ = Angles[2]


        TruckWheelPointsX = [Point for Point in APIDATA["configVector"]["truckWheelPositionX"] if Point != 0]
        TruckWheelPointsY = [Point for Point in APIDATA["configVector"]["truckWheelPositionY"] if Point != 0]
        TruckWheelPointsZ = [Point for Point in APIDATA["configVector"]["truckWheelPositionZ"] if Point != 0]

        WheelAngles = [Angle for Angle in APIDATA["truckFloat"]["truck_wheelSteering"] if Angle != 0]
        if WheelAngles == []:
            for i in range(2):
                WheelAngles.append(0.000000001)

        WheelCoordinates = []
        for i in range(len(TruckWheelPointsX)):
            PointX = TruckX + TruckWheelPointsX[i] * math.cos(TruckRotationRadiansX) - TruckWheelPointsZ[i] * math.sin(TruckRotationRadiansX)
            PointY = TruckY + TruckWheelPointsY[i]
            PointZ = TruckZ + TruckWheelPointsZ[i] * math.cos(TruckRotationRadiansX) + TruckWheelPointsX[i] * math.sin(TruckRotationRadiansX)
            WheelCoordinates.append((PointX, PointY, PointZ))


        if len(WheelCoordinates) >= 4 and len(WheelAngles) >= 2:
            FrontLeftWheel = WheelCoordinates[0]
            FrontRightWheel = WheelCoordinates[1]

            BackLeftWheels = []
            BackRightWheels = []

            for i in range(len(WheelCoordinates)):
                if len(WheelAngles) > i:
                    continue

                if i % 2 == 0:
                    BackLeftWheels.append(WheelCoordinates[i])
                else:
                    BackRightWheels.append(WheelCoordinates[i])

            BackLeftWheel = (0, 0, 0)
            BackRightWheel = (0, 0, 0)

            for Wheel in BackLeftWheels:
                BackLeftWheel = BackLeftWheel[0] + Wheel[0], BackLeftWheel[1] + Wheel[1], BackLeftWheel[2] + Wheel[2]

            for Wheel in BackRightWheels:
                BackRightWheel = BackRightWheel[0] + Wheel[0], BackRightWheel[1] + Wheel[1], BackRightWheel[2] + Wheel[2]

            BackLeftWheel = BackLeftWheel[0] / len(BackLeftWheels), BackLeftWheel[1] / len(BackLeftWheels), BackLeftWheel[2] / len(BackLeftWheels)
            BackRightWheel = BackRightWheel[0] / len(BackRightWheels), BackRightWheel[1] / len(BackRightWheels), BackRightWheel[2] / len(BackRightWheels)

            FrontLeftSteerAngle = WheelAngles[0] * 360
            FrontRightSteerAngle = WheelAngles[1] * 360

            DistanceLeft = math.sqrt((FrontLeftWheel[0] - BackLeftWheel[0]) ** 2 + (FrontLeftWheel[2] - BackLeftWheel[2]) ** 2)
            DistanceRight = math.sqrt((FrontRightWheel[0] - BackRightWheel[0]) ** 2 + (FrontRightWheel[2] - BackRightWheel[2]) ** 2)

            LeftFrontWheelRadius = CalculateRadiusFrontWheel(FrontLeftSteerAngle, DistanceLeft)
            LeftBackWheelRadius = CalculateRadiusBackWheel(FrontLeftSteerAngle, DistanceLeft)
            RightFrontWheelRadius = CalculateRadiusFrontWheel(FrontRightSteerAngle, DistanceRight)
            RightBackWheelRadius = CalculateRadiusBackWheel(FrontRightSteerAngle, DistanceRight)

            LeftCenterX = BackLeftWheel[0] - LeftBackWheelRadius * math.cos(TruckRotationRadiansX)
            LeftCenterZ = BackLeftWheel[2] - LeftBackWheelRadius * math.sin(TruckRotationRadiansX)
            RightCenterX = BackRightWheel[0] - RightBackWheelRadius * math.cos(TruckRotationRadiansX)
            RightCenterZ = BackRightWheel[2] - RightBackWheelRadius * math.sin(TruckRotationRadiansX)

            LeftPoints = []
            RightPoints = []
            for i in range(2):
                if i == 0:
                    R = LeftFrontWheelRadius - 1
                    CenterX = LeftCenterX
                    CenterZ = LeftCenterZ
                    Offset = math.degrees(math.atan((DistanceLeft + 5) / R))
                else:
                    R = RightFrontWheelRadius + 1
                    CenterX = RightCenterX
                    CenterZ = RightCenterZ
                    Offset = math.degrees(math.atan((DistanceRight + 5) / R))
                for j in range(15):
                    Angle = j * (1 / -R) * 120 - TruckRotationDegreesX - Offset
                    Angle = math.radians(Angle)
                    X = CenterX + R * math.cos(Angle)
                    Z = CenterZ + R * math.sin(Angle)
                    Distance = math.sqrt((X - TruckX) ** 2 + (Z - TruckZ) ** 2)
                    Y = TruckY + math.tan(math.radians(TruckRotationY * 360)) * Distance
                    X, Y, D = ConvertToScreenCoordinate(X=X, Y=Y, Z=Z)
                    if X != None and Y != None:
                        if i == 0:
                            LeftPoints.append([X, Y])
                        else:
                            RightPoints.append([X, Y])

            TotalImage = np.zeros((100 * min(len(LeftPoints) - 1, len(RightPoints) - 1), 500, 3), np.uint8)
            for i in range(min(len(LeftPoints) - 1, len(RightPoints) - 1)):
                BottomLeft = LeftPoints[i]
                TopLeft = LeftPoints[i + 1]
                BottomRight = RightPoints[i]
                TopRight = RightPoints[i + 1]

                CroppedWidth = 500
                CroppedHeight = 100
                SourcePoints = np.float32([TopLeft, TopRight, BottomLeft, BottomRight])
                DestinationPoints = np.float32([[0, 0], [CroppedWidth, 0], [0, CroppedHeight], [CroppedWidth, CroppedHeight]])
                Matrix = cv2.getPerspectiveTransform(SourcePoints, DestinationPoints)
                Image = cv2.warpPerspective(Frame, Matrix, (CroppedWidth, CroppedHeight))
                TotalImage[TotalImage.shape[0] - (i + 1) * 100:TotalImage.shape[0] - i * 100] = Image

            Frame = TotalImage.copy()

            if Enabled == True:
                Output = Model.detect(Frame)

                Value = min(max(0, Output[0][0]), 1)

                ValueHistory.append((Value, CurrentTime))
                ValueHistory.sort(key=lambda x: x[1])
                while CurrentTime - ValueHistory[0][1] > 0.5:
                    ValueHistory.pop(0)
                Value = sum(x[0] for x in ValueHistory) / len(ValueHistory)

                cv2.rectangle(Frame, (0, 0), (Frame.shape[1] - 1, Frame.shape[0] - 1), (0, 255, 0), 2)
                cv2.line(Frame, (0, round(Frame.shape[0] * Value)), (Frame.shape[1] - 1, round(Frame.shape[0] * Value)), (0, 0, 255), 2)

                if Value < 0.5:
                    SDKController.aforward = float(math.sqrt(max(0, 0.5 - Value * 2))) if APIDATA["truckFloat"]["speed"] < APIDATA["truckFloat"]["speedLimit"] + 2 else float(0)
                    SDKController.abackward = float(0)
                else:
                    SDKController.aforward = float(0)
                    SDKController.abackward = float((Value - 0.5) ** 2)
            else:
                cv2.rectangle(Frame, (0, 0), (Frame.shape[1] - 1, Frame.shape[0] - 1), (0, 0, 255), 2)
                SDKController.aforward = float(0)
                SDKController.abackward = float(0)

        ShowImage.Show("AdaptiveCruiseControl", Frame)