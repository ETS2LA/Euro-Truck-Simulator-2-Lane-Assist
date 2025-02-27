from ETS2LA.Plugin import *
from ETS2LA.UI import *

from Plugins.AR.classes import *
from ETS2LA.Utils.Values.numbers import SmoothedValue

PURPLE = "\033[95m"
NORMAL = "\033[0m"
DRAWLIST = []
TELEMETRY_FPS = SmoothedValue("time", 1)

def InitializeWindow():
    global regular_font
    
    WindowX1, WindowY1, WindowX2, WindowY2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])


    dpg.create_context()
    with dpg.font_registry():
        regular_font = dpg.add_font('Plugins/AR/Geist-Regular.ttf', 32, default_font=True)
        #bold_font = dpg.add_font('Roboto-Bold.ttf', 20)
    
    dpg.create_viewport(title=f"ETS2LA AR Overlay", always_on_top=True, decorated=False, clear_color=[0.0,0.0,0.0,0.0], vsync=False, x_pos=WindowX1, y_pos=WindowY1, width=WindowX2-WindowX1, height=WindowY2-WindowY1, small_icon=variables.ICONPATH, large_icon=variables.ICONPATH)
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

    SetWindowDisplayAffinity = ctypes.windll.user32.SetWindowDisplayAffinity
    SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
    SetWindowDisplayAffinity.restype = wintypes.BOOL
    Success = SetWindowDisplayAffinity(HWND, 0x00000011)
    if Success == 0:
        print("Failed to hide AR window from screen capture.")


def Resize():
    dpg.set_viewport_pos([WindowPosition[0], WindowPosition[1]])
    dpg.set_viewport_width(WindowPosition[2] - WindowPosition[0])
    dpg.set_viewport_height(WindowPosition[3] - WindowPosition[1])


def CalculateAlpha(Distances=[], fade_end=10, fade_start=30, max_fade_start=150, max_fade_end=170):
    # Filter out None values from the Distances list
    Distances = [Distance for Distance in Distances if Distance is not None]
    
    # If no valid distances, return 0
    if len(Distances) == 0:
        return 0
    
    # Calculate the average distance
    AverageDistance = sum(Distances) / len(Distances)
    
    # Determine the alpha value based on the average distance
    if AverageDistance < fade_end:
        return 0
    elif fade_end <= AverageDistance < fade_start:
        return (255 * (AverageDistance - fade_end) / (fade_start - fade_end))
    elif fade_start <= AverageDistance < max_fade_start:
        return 255
    elif max_fade_start <= AverageDistance < max_fade_end:
        return (255 * (max_fade_end - AverageDistance) / (max_fade_end - max_fade_start))
    else:
        return 0


def ConvertToScreenCoordinate(X: float, Y: float, Z: float, relative: bool = False, head_relative: bool = False):
    HeadYaw = HeadRotationDegreesX
    HeadPitch = HeadRotationDegreesY
    HeadRoll = HeadRotationDegreesZ

    if relative:
        RelativeX = X - InsideHeadX - HeadX
        RelativeY = Y - InsideHeadY - HeadY
        RelativeZ = Z - InsideHeadZ - HeadZ
        
        if head_relative:
            # Rotate the points around the head (0, 0, 0)
            CosPitch = math.cos(math.radians(CabinOffsetRotationDegreesY))
            SinPitch = math.sin(math.radians(CabinOffsetRotationDegreesY))
            NewY = RelativeY * CosPitch - RelativeZ * SinPitch
            NewZ = RelativeZ * CosPitch + RelativeY * SinPitch

            CosYaw = math.cos(math.radians(CabinOffsetRotationDegreesX))
            SinYaw = math.sin(math.radians(CabinOffsetRotationDegreesX))
            NewX = RelativeX * CosYaw + NewZ * SinYaw
            NewZ = NewZ * CosYaw - RelativeX * SinYaw

            CosRoll = math.cos(math.radians(0))#-CabinOffsetRotationDegreesZ))
            SinRoll = math.sin(math.radians(0))#-CabinOffsetRotationDegreesZ))
            FinalX = NewX * CosRoll - NewY * SinRoll
            FinalY = NewY * CosRoll + NewX * SinRoll

            RelativeX = FinalX
            RelativeY = FinalY
            RelativeZ = NewZ
        
    else:
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
        return None

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
        description="Overlays data on top of the game screen. Supports all plugins tagged with 'AR' (click the tag on the right). Still in development.",
        modules=["TruckSimAPI", "Camera"],
        tags=["Visualization", "AR", "Base"]
    )

    author = [Author(
        name="Glas42",
        url="https://github.com/OleFranz",
        icon="https://avatars.githubusercontent.com/u/145870870?v=4"
    ), Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )]

    fps_cap = 1000
    camera = None
    last_camera_timestamp = 0
    LastTimeStamp = 0

    def imports(self):
        global SCSTelemetry, ScreenCapture, settings, variables, dpg, wintypes, win32con, win32gui, ctypes, math, time

        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        import ETS2LA.Utils.settings as settings
        import ETS2LA.variables as variables

        import dearpygui.dearpygui as dpg
        from ctypes import wintypes
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
            print(f"\n{PURPLE}Make sure to set the FOV in the global settings (Settings -> Global -> Variables) if you are not using the newest game version!{NORMAL}\n")
            self.notify("Please set the FOV in the global settings (Settings -> Global -> Variables) if you are not using the newest game version!")
            FOV = 75

        InitializeWindow()

    def Render(self, items=[]):
        global FRAME
        dpg.delete_item(FRAME)
        
        distances = []
        discard = []
        for item in items:
            distance = item.get_distance(HeadX, HeadY, HeadZ)
            if distance < 1000:
                distances.append(item.get_distance(HeadX, HeadY, HeadZ))
            else:
                discard.append(item)
                
        for item in discard:
            items.remove(item)
            
        sorted_items = [item for _, item in sorted(zip(distances, items), key=lambda pair: pair[0], reverse=True)]
        
        with dpg.viewport_drawlist(label="draw") as FRAME:
            dpg.bind_font(regular_font)
            for i, item in enumerate(sorted_items):
                if type(item) == Rectangle:
                    points = [item.start, item.end]
                    start = points[0].screen(self)
                    end = points[1].screen(self)
                    
                    if start is None or end is None:
                        continue
                    
                    if type(points[0]) == Coordinate:
                        alpha = CalculateAlpha(Distances=[start[2], end[2]], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        start = start[:2]
                        end = end[:2]
                        item.color.a *= alpha / 255
                        item.fill.a *= alpha / 255
                    
                    dpg.draw_rectangle(pmin=start, pmax=end, color=item.color.tuple(), fill=item.fill.tuple(), thickness=item.thickness)
                    
                elif type(item) == Line:
                    points = [item.start, item.end]
                    start = points[0].screen(self)
                    end = points[1].screen(self)
                    
                    if start is None or end is None:
                        continue
                    
                    if type(points[0]) == Coordinate:
                        alpha = CalculateAlpha(Distances=[start[2], end[2]], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        start = start[:2]
                        end = end[:2]
                        item.color.a *= alpha / 255
                    
                    dpg.draw_line(p1=start, p2=end, color=item.color.tuple(), thickness=item.thickness)
                    
                elif type(item) == Polygon:
                    points = item.points
                    points = [point.screen(self) for point in item.points]
                    
                    if None in points:
                        continue
                    
                    if type(points[0]) == Coordinate:
                        alpha = CalculateAlpha(Distances=[point[2] for point in points], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        points = [point[:2] for point in points]
                        item.color.a *= alpha / 255
                        item.fill.a *= alpha / 255
                    
                    dpg.draw_polygon(points=points, color=item.color.tuple(), fill=item.fill.tuple(), thickness=item.thickness)
                    
                elif type(item) == Circle:
                    center = item.center
                    center = center.screen(self)
                    
                    if center is None:
                        continue
                    
                    if type(center) == Coordinate:
                        alpha = CalculateAlpha(Distances=[center[2]], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        center = center[:2]
                        item.color.a *= alpha / 255
                        item.fill.a *= alpha / 255
                        center = center[:2]
                    
                    dpg.draw_circle(center=center, radius=item.radius, color=item.color.tuple(), fill=item.fill.tuple(), thickness=item.thickness)
                    
                elif type(item) == Text:
                    position = item.point
                    position = position.screen(self)
                    
                    if position is None:
                        continue
                    
                    if type(position) == Coordinate:
                        alpha = CalculateAlpha(Distances=[position[2]], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        position = position[:2]
                        item.color.a *= alpha / 255
                        position = position[:2]
                    
                    dpg.draw_text(position, text=item.text, color=item.color.tuple(), size=item.size)
                 
        dpg.render_dearpygui_frame()

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
        global InsideHeadX
        global InsideHeadY
        global InsideHeadZ
        
        global TruckRotationDegreesX
        global TruckRotationDegreesY
        global TruckRotationDegreesZ
        
        global CabinOffsetRotationDegreesX
        global CabinOffsetRotationDegreesY
        global CabinOffsetRotationDegreesZ

        APIDATA = TruckSimAPI.update()
        
        if APIDATA["pause"] == True or ScreenCapture.IsForegroundWindow(Name="Truck Simulator", Blacklist=["Discord"]) == False:
            time.sleep(0.1)
            self.Render()
            return
        
        if APIDATA["renderTime"] == self.LastTimeStamp:
            return
        else:
            # 166660.0 -> 60 FPS -> Unit is in microseconds
            microseconds = (APIDATA["renderTime"] - self.LastTimeStamp)
            TELEMETRY_FPS.smooth(1 / (microseconds / 1000000))
            #print(f"Telemetry FPS: {TELEMETRY_FPS.get():.1f}         ", end="\r")
            self.LastTimeStamp = APIDATA["renderTime"]
            

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

        TruckRotationDegreesY = TruckRotationY * 360
        TruckRotationDegreesZ = TruckRotationZ * 180
        
        CabinOffsetRotationDegreesX = (TruckRotationX + CabinOffsetRotationX) * 360
        CabinOffsetRotationDegreesY = (TruckRotationY + CabinOffsetRotationY) * 360
        CabinOffsetRotationDegreesZ = (TruckRotationZ + CabinOffsetRotationZ) * 180

        HeadRotationDegreesX = (TruckRotationX + CabinOffsetRotationX + HeadOffsetRotationX) * 360
        while HeadRotationDegreesX > 360:
            HeadRotationDegreesX = HeadRotationDegreesX - 360

        HeadRotationDegreesY = (TruckRotationY + CabinOffsetRotationY) * 180 + (HeadOffsetRotationY) * 360

        HeadRotationDegreesZ = (TruckRotationZ + CabinOffsetRotationZ + HeadOffsetRotationZ) * 180

        PointX = HeadOffsetX
        PointY = HeadOffsetY
        PointZ = HeadOffsetZ
        
        InsideHeadX = PointX * math.cos(TruckRotationRadiansX) - PointZ * math.sin(TruckRotationRadiansX) + TruckX
        InsideHeadY = PointY + TruckY
        InsideHeadZ = PointX * math.sin(TruckRotationRadiansX) + PointZ * math.cos(TruckRotationRadiansX) + TruckZ
        
        camera = self.modules.Camera.run()
        if camera is not None:
            FOV = camera.fov
            angles = camera.rotation.euler()
            HeadX = camera.position.x + camera.cx * 512
            HeadY = camera.position.y
            HeadZ = camera.position.z + camera.cz * 512
            HeadRotationDegreesX = angles[1]
            HeadRotationDegreesY = angles[0]
            HeadRotationDegreesZ = angles[2]
        else:
            HeadX = InsideHeadX
            HeadY = InsideHeadY
            HeadZ = InsideHeadZ

        # Update self so that coordinates can pull in the variables
        self.LastWindowPosition = LastWindowPosition
        self.WindowPosition = WindowPosition
        self.HeadRotationDegreesX = HeadRotationDegreesX
        self.HeadRotationDegreesY = HeadRotationDegreesY
        self.HeadRotationDegreesZ = HeadRotationDegreesZ
        self.HeadX = HeadX
        self.HeadY = HeadY
        self.HeadZ = HeadZ
        self.InsideHeadX = InsideHeadX
        self.InsideHeadY = InsideHeadY
        self.InsideHeadZ = InsideHeadZ
        self.TruckRotationDegreesX = TruckRotationDegreesX
        self.TruckRotationDegreesY = TruckRotationDegreesY
        self.TruckRotationDegreesZ = TruckRotationDegreesZ
        self.CabinOffsetRotationDegreesX = CabinOffsetRotationDegreesX
        self.CabinOffsetRotationDegreesY = CabinOffsetRotationDegreesY
        self.CabinOffsetRotationDegreesZ = CabinOffsetRotationDegreesZ
        self.DRAWLIST = DRAWLIST
        self.FOV = FOV

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
            #X, Y, D = ConvertToScreenCoordinate(X=PointX, Y=PointY, Z=PointZ)
            
            DRAWLIST.append(Circle(
                center=Coordinate(PointX, PointY, PointZ),
                radius=10,
                color=Color(255, 255, 255, 255),
                fill=Color(127, 127, 127, 127),
                fade=Fade(prox_fade_start=0, prox_fade_end=0, dist_fade_start=100, dist_fade_end=100),
                thickness=2
            ))


        DRAWLIST.append(Polygon(
            points=[
                Coordinate(10353.160, 48.543, -9228.122),
                Coordinate(10352.160, 47.543, -9224.122),
                Coordinate(10353.160, 46.543, -9228.122),
                Coordinate(10353.160, 48.543, -9228.122)
            ],
            color=Color(255, 255, 255, 255),
            fill=Color(127, 127, 127, 255 / 2),
            thickness=2
        ))

        other_plugins = self.globals.tags.AR
        if other_plugins is not None:
            for plugin in other_plugins:
                if type(other_plugins[plugin]) == list:
                    DRAWLIST.extend(other_plugins[plugin])
        
        self.Render(items=DRAWLIST)
        DRAWLIST = []