from ETS2LA.Plugin import *
from ETS2LA.UI import *


PURPLE = "\033[95m"
NORMAL = "\033[0m"


def InitializeWindow():
    WindowX1, WindowY1, WindowX2, WindowY2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])

    dpg.create_context()
    dpg.create_viewport(title=f"ETS2LA AR Overlay", always_on_top=True, decorated=False, clear_color=[0.0,0.0,0.0,0.0], vsync=False, x_pos=WindowX1, y_pos=WindowY1, width=WindowX2-WindowX1, height=WindowY2-WindowY1, small_icon=f"{variables.PATH}Interface/assets/favicon.ico", large_icon=f"{variables.PATH}Interface/assets/favicon.ico")
    dpg.set_viewport_always_top(True)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    class MARGINS(ctypes.Structure):
        _fields_ = [("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int)]

    HWND = win32gui.FindWindow(None, "ETS2LA AR Overlay")
    Margins = MARGINS(-1, -1, -1, -1)
    ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(HWND, Margins)
    win32gui.SetWindowLong(HWND, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(HWND, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)


def Resize():
    dpg.set_viewport_pos([WindowPosition[0], WindowPosition[1]])
    dpg.set_viewport_width(WindowPosition[2] - WindowPosition[0])
    dpg.set_viewport_height(WindowPosition[3] - WindowPosition[1])


def DrawRectangle(Start=[0, 0], End=[100, 100], Color=[255, 255, 255, 255], FillColor=[0, 0, 0, 0], Thickness=1):
    global DRAWLIST
    FillColor = list(FillColor)
    Color = list(Color)
    if len(FillColor) <= 3:
        FillColor.append(255)
    if len(Color) <= 3:
        Color.append(255)
    DRAWLIST.append(("Rectangle", Start, End, Color, FillColor, Thickness))


def DrawLine(Start=[0, 0], End=[100, 100], Color=[255, 255, 255, 255], Thickness=1):
    global DRAWLIST
    Color = list(Color)
    if len(Color) <= 3:
        Color.append(255)
    DRAWLIST.append(("Line", Start, End, Color, Thickness))


def DrawPolygon(Points=[(100, 0), (100, 100), (0, 100)], Color=[255, 255, 255, 255], FillColor=[0, 0, 0, 0], Thickness=1, Closed=False):
    global DRAWLIST
    FillColor = list(FillColor)
    Color = list(Color)
    if len(FillColor) <= 3:
        FillColor.append(255)
    if len(Color) <= 3:
        Color.append(255)
    Points = [(X, Y) for X, Y in Points if X != None and Y != None]
    if len(Points) <= 1:
        return
    if Closed:
        if Points[0] != Points[-1]:
            Points.append(Points[0])
    DRAWLIST.append(("Polygon", Points, Color, FillColor, Thickness))


def DrawCircle(Center=[0, 0], R=100, Color=[255, 255, 255, 255], FillColor=[0, 0, 0, 0], Thickness=1):
    global DRAWLIST
    Color = list(Color)
    if len(Color) <= 3:
        Color.append(255)
    DRAWLIST.append(("Circle", Center, R, Color, FillColor, Thickness))


def Render():
    global FRAME
    global DRAWLIST
    dpg.delete_item(FRAME)
    with dpg.viewport_drawlist(label="draw") as FRAME:
        for Item in DRAWLIST:
            if Item[0] == "Rectangle":
                dpg.draw_rectangle(pmin=Item[1], pmax=Item[2], color=Item[3], fill=Item[4], thickness=Item[5])
            elif Item[0] == "Line":
                dpg.draw_line(p1=Item[1], p2=Item[2], color=Item[3], thickness=Item[4])
            elif Item[0] == "Polygon":
                dpg.draw_polygon(points=Item[1], color=Item[2], fill=Item[3], thickness=Item[4])
            elif Item[0] == "Circle":
                dpg.draw_circle(center=Item[1], radius=Item[2], color=Item[3], fill=Item[4], thickness=Item[5])
    dpg.render_dearpygui_frame()
    DRAWLIST = []


def CalculateAlpha(Distances=[]):
    Distances = [Distance for Distance in Distances if Distance != None]
    if len(Distances) == 0:
        return 0
    AverageDistance = sum(Distances) / len(Distances)
    if AverageDistance < 10:
        return 0
    elif 10 <= AverageDistance < 30:
        return (255 * (AverageDistance - 10) / 20)
    elif 30 <= AverageDistance < 150:
        return 255
    elif 150 <= AverageDistance < 170:
        return (255 * (170 - AverageDistance) / 20)
    else:
        return 0


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
    
    WindowDistance = ((WindowPosition[3] - WindowPosition[1]) * (4 / 3) / 2) / math.tan(FovRad / 2)

    ScreenX = (FinalX / FinalZ) * WindowDistance + (WindowPosition[2] - WindowPosition[0]) / 2
    ScreenY = (FinalY / FinalZ) * WindowDistance + (WindowPosition[3] - WindowPosition[1]) / 2

    ScreenX = (WindowPosition[2] - WindowPosition[0]) - ScreenX

    Distance = math.sqrt((RelativeX ** 2) + (RelativeY ** 2) + (RelativeZ ** 2))

    return ScreenX, ScreenY, Distance


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="AR",
        version="1.0",
        description="In Development.",
        modules=["TruckSimAPI"]
    )

    author = Author(
        name="Glas42",
        url="https://github.com/Glas42",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    )

    fps_cap = 1000


    def imports(self):
        global SCSTelemetry, ScreenCapture, settings, variables, dpg, win32con, win32gui, ctypes, math, time

        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        import ETS2LA.Utils.settings as settings
        import ETS2LA.variables as variables

        import dearpygui.dearpygui as dpg
        import win32con
        import win32gui
        import ctypes
        import math
        import time

        global LastWindowPosition
        global TruckSimAPI
        global DRAWLIST
        global FRAME
        global FOV

        LastWindowPosition = None, None, None, None
        TruckSimAPI = SCSTelemetry()
        DRAWLIST = []
        FRAME = None
        FOV = self.globals.settings.FOV
        if FOV == None:
            print(f"\n{PURPLE}Make sure to set the FOV in the settings for AR! The plugin will disable itself.{NORMAL}\n")
            self.notify("No FOV set, disabling AR...")
            self.terminate()

        InitializeWindow()


    def run(self):
        global LastWindowPosition
        global WindowPosition

        global HeadRotationDegreesX
        global HeadRotationDegreesY
        global HeadRotationDegreesZ
        global HeadX
        global HeadY
        global HeadZ

        APIDATA = TruckSimAPI.update()

        if APIDATA["pause"] == True or ScreenCapture.IsForegroundWindow(Name="Truck Simulator", Blacklist=["Discord"]) == False:
            time.sleep(0.1)
            Render()
            return

        WindowPosition = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
        if LastWindowPosition != WindowPosition:
            Resize()


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


        # Draws a circle at each wheel of the truck
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
            DrawCircle(Center=(X, Y), R=10, Color=(255, 255, 255), FillColor=(127, 127, 127, 127), Thickness=2)


        # The arrow at the berlin spawn
        X1, Y1, D1 = ConvertToScreenCoordinate(X=10353.160, Y=48.543, Z=-9228.122)
        X2, Y2, D2 = ConvertToScreenCoordinate(X=10352.160, Y=47.543, Z=-9224.122)
        X3, Y3, D3 = ConvertToScreenCoordinate(X=10353.160, Y=46.543, Z=-9228.122)
        Alpha = CalculateAlpha(Distances=[D1, D2, D3])
        DrawPolygon(Points=[(X1, Y1), (X2, Y2), (X3, Y3)], Color=(255, 255, 255, Alpha), FillColor=(127, 127, 127, Alpha / 2), Thickness=2, Closed=True)


        Render()