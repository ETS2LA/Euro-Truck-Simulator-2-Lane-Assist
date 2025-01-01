from ETS2LA.Plugin import *
from ETS2LA.UI import *

from Plugins.AR.classes import *

PURPLE = "\033[95m"
NORMAL = "\033[0m"
DRAWLIST = []

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


def Render(Items=[]):
    global FRAME
    dpg.delete_item(FRAME)
    with dpg.viewport_drawlist(label="draw") as FRAME:
        for Item in Items:
            if type(Item) == Rectangle:
                start = Item.start.tuple() if type(Item.start) == Point else ConvertToScreenCoordinate(*Item.start.tuple())
                end = Item.end.tuple() if type(Item.end) == Point else ConvertToScreenCoordinate(*Item.end.tuple())
                if start is None or end is None:
                    continue
                dpg.draw_rectangle(pmin=start, pmax=end, color=Item.color.tuple(), fill=Item.fill.tuple(), thickness=Item.thickness)
                
            elif type(Item) == Line:
                start = Item.start.tuple() if type(Item.start) == Point else ConvertToScreenCoordinate(*Item.start.tuple())
                end = Item.end.tuple() if type(Item.end) == Point else ConvertToScreenCoordinate(*Item.end.tuple())
                if start is None or end is None:
                    continue
                dpg.draw_line(p1=start, p2=end, color=Item.color.tuple(), thickness=Item.thickness)
                
            elif type(Item) == Polygon:
                points = [(point.tuple() if type(point) == Point else ConvertToScreenCoordinate(*point.tuple())) for point in Item.points]
                if (None, None) in points or (None, None, None) in points:
                    continue
                dpg.draw_polygon(points=points, color=Item.color.tuple(), fill=Item.fill.tuple(), thickness=Item.thickness)
                
            elif type(Item) == Circle:
                center = Item.center.tuple() if type(Item.center) == Point else ConvertToScreenCoordinate(*Item.center.tuple())
                if center is None:
                    continue
                dpg.draw_circle(center=center, radius=Item.radius, color=Item.color.tuple(), fill=Item.fill.tuple(), thickness=Item.thickness)
                
    dpg.render_dearpygui_frame()


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
            print(f"\n{PURPLE}Make sure to set the FOV in the global settings (Settings -> Global -> Variables)! The plugin will disable itself.{NORMAL}\n")
            self.notify("No FOV set, disabling AR...")
            self.terminate()

        InitializeWindow()


    def run(self):
        global DRAWLIST
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
            LastWindowPosition = WindowPosition
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

        HeadRotationDegreesZ = (-TruckRotationZ + CabinOffsetRotationZ + HeadOffsetRotationZ) * 360

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
            
            DRAWLIST.append(Circle(
                center=Point(X, Y),
                radius=10,
                color=Color(255, 255, 255, 255),
                fill=Color(127, 127, 127, 127),
                thickness=2
            ))


        # The arrow at the berlin spawn
        X1, Y1, D1 = ConvertToScreenCoordinate(X=10353.160, Y=48.543, Z=-9228.122)
        X2, Y2, D2 = ConvertToScreenCoordinate(X=10352.160, Y=47.543, Z=-9224.122)
        X3, Y3, D3 = ConvertToScreenCoordinate(X=10353.160, Y=46.543, Z=-9228.122)
        Alpha = CalculateAlpha(Distances=[D1, D2, D3])
        DRAWLIST.append(Polygon(
            points=[Point(X1, Y1), Point(X2, Y2), Point(X3, Y3), Point(X1, Y1)],
            color=Color(255, 255, 255, Alpha),
            fill=Color(127, 127, 127, Alpha / 2),
            thickness=2
        ))

        other_plugins = self.globals.tags.AR
        if other_plugins is not None:
            for plugin in other_plugins:
                if type(other_plugins[plugin]) == list:
                    DRAWLIST.extend(other_plugins[plugin])

        Render(Items=DRAWLIST)
        DRAWLIST = []