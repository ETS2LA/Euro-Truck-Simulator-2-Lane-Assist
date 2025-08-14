from ETS2LA.Plugin import *
from ETS2LA.UI import *
import math
import time
import cv2
import numpy as np

PURPLE = "\033[95m"
NORMAL = "\033[0m"

# 新增变道控制参数
SAFE_DISTANCE = 15.0  # 安全变道距离(米)
MIN_SPEED_FOR_LANE_CHANGE = 20.0  # 允许变道的最低速度(km/h)
LANE_CHANGE_DURATION = 2.5  # 变道持续时间(秒)
LANE_CHANGE_TRIGGER_DELAY = 0.3  # 转向灯触发后的延迟时间(秒)

class LaneChangeController:
    def __init__(self):
        self.state = "IDLE"  # IDLE, PREPARING, CHANGING
        self.direction = None  # LEFT, RIGHT
        self.start_time = 0
        self.target_lateral_offset = 0.0
        self.current_lateral_offset = 0.0
        self.lane_width = 3.5  # 标准车道宽度(米)

    def update(self, turn_signal, current_speed, dt):
        """更新变道状态机"""
        # 检查是否满足变道基本条件
        if current_speed < MIN_SPEED_FOR_LANE_CHANGE * 0.2778:  # 转换为m/s
            self.state = "IDLE"
            return 0.0

        # 状态转换逻辑
        if self.state == "IDLE":
            if turn_signal == "LEFT":
                self.state = "PREPARING"
                self.direction = "LEFT"
                self.start_time = time.time()
                self.target_lateral_offset = -self.lane_width
            elif turn_signal == "RIGHT":
                self.state = "PREPARING"
                self.direction = "RIGHT"
                self.start_time = time.time()
                self.target_lateral_offset = self.lane_width

        elif self.state == "PREPARING":
            # 等待短暂延迟后开始变道
            if time.time() - self.start_time > LANE_CHANGE_TRIGGER_DELAY:
                self.state = "CHANGING"
                self.start_time = time.time()

        elif self.state == "CHANGING":
            # 计算变道进度(0-1)
            progress = min(1.0, (time.time() - self.start_time) / LANE_CHANGE_DURATION)

            # 使用S型曲线实现平滑变道
            progress = 1 / (1 + math.exp(-12 * (progress - 0.5)))

            # 计算当前横向偏移
            self.current_lateral_offset = self.target_lateral_offset * progress

            # 变道完成
            if progress >= 1.0:
                self.state = "IDLE"
                self.direction = None

        # 重置条件
        if self.state != "IDLE" and turn_signal == "OFF":
            self.state = "IDLE"
            self.direction = None

        return self.current_lateral_offset

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
        tags=["Steering"],
        fps_cap=500
    )

    author = Author(
        name="Glas42",
        url="https://github.com/OleFranz",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )


    def imports(self):
        global SCSTelemetry, SCSController, ScreenCapture, ShowImage, variables, settings, pytorch, np, keyboard, math, time, cv2

        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        from Modules.SDKController.main import SCSController
        import Modules.BetterShowImage.main as ShowImage
        import ETS2LA.Handlers.pytorch as pytorch
        import ETS2LA.Utils.settings as settings
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
        global SteeringHistory

        global Model

        global SDKController
        global TruckSimAPI

        FOV = self.globals.settings.FOV
        if FOV == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for End-To-End! The plugin will disable itself.{NORMAL}\n")
            self.notify("No FOV set, disabling End-To-End...")
            time.sleep(1)
            self.terminate()
        Enabled = True
        EnableKey = settings.Get("Steering", "EnableKey", "n")
        EnableKeyPressed = False
        LastEnableKeyPressed = False
        SteeringHistory = []

        Model = pytorch.Model(HF_owner="OleFranz", HF_repository="End-To-End", HF_model_folder="model", plugin_self=self, torch_dtype=pytorch.torch.float32)
        Model.load_model()

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

        EnableKeyPressed = keyboard.is_pressed(EnableKey)
        if EnableKeyPressed == False and LastEnableKeyPressed == True:
            Enabled = not Enabled
        LastEnableKeyPressed = EnableKeyPressed

        Output = [[0] * Model.outputs]

        if Enabled == True:
            if Model.loaded == True:
                Output = Model.detect(Frame)

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
