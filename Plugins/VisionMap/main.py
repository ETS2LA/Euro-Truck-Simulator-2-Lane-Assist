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

    CosRoll = math.cos(math.radians(-HeadRoll))
    SinRoll = math.sin(math.radians(-HeadRoll))
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
        name="VisionMap",
        version="1.0",
        description="In Development.",
        modules=["TruckSimAPI"]
    )

    author = Author(
        name="Glas42",
        url="https://github.com/Glas42",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 30

    def imports(self):
        global SCSTelemetry, ScreenCapture, ShowImage, variables, np, math, time, cv2

        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        import Modules.BetterShowImage.main as ShowImage
        import ETS2LA.variables as variables
        import numpy as np
        import math
        import time
        import cv2

        global FOV
        FOV = self.globals.settings.FOV
        if FOV == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for VisionMap! The plugin will disable itself.{NORMAL}\n")
            self.notify("No FOV set, disabling VisionMap...")
            self.terminate()

        global TruckSimAPI
        global LastScreenCaptureCheck
        global Images
        global FRAME

        TruckSimAPI = SCSTelemetry()

        ScreenCapture.Initialize()
        ShowImage.Initialize(Name="VisionMap", TitleBarColor=(0, 0, 0))

        LastScreenCaptureCheck = 0
        Images = []
        FRAME = np.zeros((500, 500, 3), np.uint8)

    def run(self):
        CurrentTime = time.time()

        global LastScreenCaptureCheck
        global FRAME

        global HeadRotationDegreesX
        global HeadRotationDegreesY
        global HeadRotationDegreesZ
        global HeadX
        global HeadY
        global HeadZ

        APIDATA = TruckSimAPI.update()

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

        HeadRotationDegreesZ = (TruckRotationZ + CabinOffsetRotationZ + HeadOffsetRotationZ) * 180

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


        OffsetX = 50
        OffsetZ = 14

        PointX = TruckX + OffsetX * math.sin(TruckRotationRadiansX) - OffsetZ * math.cos(TruckRotationRadiansX)
        PointY = TruckY + math.tan(math.radians(TruckRotationY * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
        PointZ = TruckZ - OffsetX * math.cos(TruckRotationRadiansX) - OffsetZ * math.sin(TruckRotationRadiansX)

        X, Y, D = ConvertToScreenCoordinate(PointX, PointY, PointZ)
        if X == None or Y == None:
            AllCoordinatesValid = False
        else:
            TopLeft = X, Y
            Points.append((PointX, PointZ))


        OffsetX = 50
        OffsetZ = -14

        PointX = TruckX + OffsetX * math.sin(TruckRotationRadiansX) - OffsetZ * math.cos(TruckRotationRadiansX)
        PointY = TruckY + math.tan(math.radians(TruckRotationY * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
        PointZ = TruckZ - OffsetX * math.cos(TruckRotationRadiansX) - OffsetZ * math.sin(TruckRotationRadiansX)

        X, Y, D = ConvertToScreenCoordinate(PointX, PointY, PointZ)
        if X == None or Y == None:
            AllCoordinatesValid = False
        else:
            TopRight = X, Y
            Points.append((PointX, PointZ))


        OffsetX = 15
        OffsetZ = 5

        PointX = TruckX + OffsetX * math.sin(TruckRotationRadiansX) - OffsetZ * math.cos(TruckRotationRadiansX)
        PointY = TruckY + math.tan(math.radians(TruckRotationY * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
        PointZ = TruckZ - OffsetX * math.cos(TruckRotationRadiansX) - OffsetZ * math.sin(TruckRotationRadiansX)

        X, Y, D = ConvertToScreenCoordinate(PointX, PointY, PointZ)
        if X == None or Y == None:
            AllCoordinatesValid = False
        else:
            BottomLeft = X, Y
            Points.append((PointX, PointZ))


        OffsetX = 15
        OffsetZ = -5

        PointX = TruckX + OffsetX * math.sin(TruckRotationRadiansX) - OffsetZ * math.cos(TruckRotationRadiansX)
        PointY = TruckY + math.tan(math.radians(TruckRotationY * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
        PointZ = TruckZ - OffsetX * math.cos(TruckRotationRadiansX) - OffsetZ * math.sin(TruckRotationRadiansX)

        X, Y, D = ConvertToScreenCoordinate(PointX, PointY, PointZ)
        if X == None or Y == None:
            AllCoordinatesValid = False
        else:
            BottomRight = X, Y
            Points.append((PointX, PointZ))


        if AllCoordinatesValid:
            try:
                CroppedWidth = round(max(TopRight[0] - TopLeft[0], BottomRight[0] - BottomLeft[0]))
                CroppedHeight = round(max(BottomLeft[1] - TopLeft[1], BottomRight[1] - TopRight[1]))
                SourcePoints = np.float32([TopLeft, TopRight, BottomLeft, BottomRight])
                DestinationPoints = np.float32([[0, 0], [CroppedWidth, 0], [0, CroppedHeight], [CroppedWidth, CroppedHeight]])
                Matrix = cv2.getPerspectiveTransform(SourcePoints, DestinationPoints)
                CroppedFrame = cv2.warpPerspective(Frame, Matrix, (CroppedWidth, CroppedHeight))

                MinX = min(Points[0][0], Points[1][0], Points[2][0], Points[3][0])
                MinZ = min(Points[0][1], Points[1][1], Points[2][1], Points[3][1])
                Scale = 12
                OnFrameX1 = (Points[0][0] - MinX) * Scale
                OnFrameY1 = (Points[0][1] - MinZ) * Scale
                OnFrameX2 = (Points[2][0] - MinX) * Scale
                OnFrameY2 = (Points[2][1] - MinZ) * Scale
                OnFrameX3 = (Points[3][0] - MinX) * Scale
                OnFrameY3 = (Points[3][1] - MinZ) * Scale
                OnFrameX4 = (Points[1][0] - MinX) * Scale
                OnFrameY4 = (Points[1][1] - MinZ) * Scale

                SourcePoints = np.float32([[0, 0], [CroppedFrame.shape[1], 0], [0, CroppedFrame.shape[0]], [CroppedFrame.shape[1], CroppedFrame.shape[0]]])
                DestinationPoints = np.float32([[OnFrameX1, OnFrameY1], [OnFrameX4, OnFrameY4], [OnFrameX2, OnFrameY2], [OnFrameX3, OnFrameY3]])
                Matrix = cv2.getPerspectiveTransform(SourcePoints, DestinationPoints)
                Frame = cv2.warpPerspective(CroppedFrame, Matrix, (500, 500), flags=cv2.INTER_NEAREST)
                Images.append((Frame, Points))
            except:
                pass

        Canvas = FRAME.copy()
        CenterX, CenterZ = 250, 250

        for i, (Image, Points) in enumerate(Images):
            MinX = min(Point[0] for Point in Points)
            MinZ = min(Point[1] for Point in Points)
            MaxX = max(Point[0] for Point in Points)
            MaxZ = max(Point[1] for Point in Points)

            CenterImageX = (MaxX + MinX) / 2
            CenterImageZ = (MaxZ + MinZ) / 2

            OffsetX = int((CenterImageX - TruckX) * 12 + CenterX - Image.shape[1] / 2)
            OffsetZ = int((CenterImageZ - TruckZ) * 12 + CenterZ - Image.shape[0] / 2)

            StartX = max(0, OffsetX)
            StartZ = max(0, OffsetZ)
            EndX = min(Canvas.shape[1], OffsetX + Image.shape[1])
            EndZ = min(Canvas.shape[0], OffsetZ + Image.shape[0])

            CropStartX = max(0, -OffsetX)
            CropStartZ = max(0, -OffsetZ)
            CropEndX = Image.shape[1] - max(0, (OffsetX + Image.shape[1]) - Canvas.shape[1])
            CropEndZ = Image.shape[0] - max(0, (OffsetZ + Image.shape[0]) - Canvas.shape[0])

            Region = Canvas[StartZ:EndZ, StartX:EndX]
            ImageRegion = Image[CropStartZ:CropEndZ, CropStartX:CropEndX]

            if Region.shape == ImageRegion.shape and ImageRegion.size > 0:
                Mask = cv2.cvtColor(ImageRegion, cv2.COLOR_BGR2GRAY) > 0
                Region[Mask] = ImageRegion[Mask]

        Frame = Canvas

        def ConvertToFrameCoordinate(X, Z):
            Scale = 12
            CenterX, CenterZ = 180, 180  # Some magic numbers, not correct

            FrameX = int((X) * Scale + CenterX)
            FrameZ = int((Z) * Scale + CenterZ)

            return FrameX, FrameZ

        for i in range(len(TruckWheelPointsX)):
            PointX = TruckWheelPointsX[i] * math.cos(TruckRotationRadiansX) - TruckWheelPointsZ[i] * math.sin(TruckRotationRadiansX)
            PointY = TruckY + TruckWheelPointsY[i]
            PointZ = TruckWheelPointsZ[i] * math.cos(TruckRotationRadiansX) + TruckWheelPointsX[i] * math.sin(TruckRotationRadiansX)
            cv2.circle(Frame, [*ConvertToFrameCoordinate(PointX, PointZ)], 5, (0, 0, 255), 2)

        ShowImage.Show(Name="VisionMap", Frame=Frame)