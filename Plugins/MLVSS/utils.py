import Modules.BetterScreenCapture.main as ScreenCapture
import variables as MLVSSVariables
import threading
import math


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

    FovRad = math.radians(MLVSSVariables.FOV)
    
    WindowDistance = ((ScreenCapture.MonitorY2 - ScreenCapture.MonitorY1) * (4 / 3) / 2) / math.tan(FovRad / 2)

    ScreenX = (FinalX / FinalZ) * WindowDistance + (ScreenCapture.MonitorX2 - ScreenCapture.MonitorX1) / 2
    ScreenY = (FinalY / FinalZ) * WindowDistance + (ScreenCapture.MonitorY2 - ScreenCapture.MonitorY1) / 2

    ScreenX = (ScreenCapture.MonitorX2 - ScreenCapture.MonitorX1) - ScreenX

    Distance = math.sqrt((RelativeX ** 2) + (RelativeY ** 2) + (RelativeZ ** 2))

    return ScreenX, ScreenY, Distance


def UpdateAPI():
    global TruckRotationDegreesX
    global TruckRotationDegreesY
    global TruckRotationDegreesZ
    global TruckRotationRadiansX
    global TruckRotationRadiansY
    global TruckRotationRadiansZ
    global TruckRotationX
    global TruckRotationY
    global TruckRotationZ
    global TruckX
    global TruckY
    global TruckZ
    global HeadRotationDegreesX
    global HeadRotationDegreesY
    global HeadRotationDegreesZ
    global HeadX
    global HeadY
    global HeadZ
    global TruckWheels
    global TruckWheelAngles

    APIDATA = MLVSSVariables.TruckSimAPI.update()

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
    TruckRotationDegreesY = TruckRotationY * 360
    TruckRotationDegreesZ = TruckRotationZ * 180
    TruckRotationRadiansX = -math.radians(TruckRotationDegreesX)
    TruckRotationRadiansY = -math.radians(TruckRotationDegreesY)
    TruckRotationRadiansZ = -math.radians(TruckRotationDegreesZ)

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
    TruckWheels = []
    for i in range(len(TruckWheelPointsX)):
        TruckWheels.append((TruckWheelPointsX[i], TruckWheelPointsY[i], TruckWheelPointsZ[i]))

    TruckWheelAngles = [Angle for Angle in APIDATA["truckFloat"]["truck_wheelSteering"] if Angle != 0]
    while int(APIDATA["configUI"]["truckWheelCount"]) > len(TruckWheelAngles):
        TruckWheelAngles.append(0)


def Launch(Plugin):
    def RunPlugin(Plugin):
        while True:
            Plugin.Run()
    threading.Thread(target=RunPlugin, args=(Plugin,), daemon=True).start()