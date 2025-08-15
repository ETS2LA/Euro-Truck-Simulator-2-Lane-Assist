from ETS2LA.Plugin import *
from ETS2LA.UI import *
from ETS2LA.UI import Text as UIText

from ETS2LA.Utils.Values.numbers import SmoothedValue
import ETS2LA.Utils.settings as settings
from ETS2LA.Utils.translator import _
from Plugins.AR.classes import *


PURPLE = "\033[95m"
NORMAL = "\033[0m"
DRAWLIST = []
TELEMETRY_FPS = SmoothedValue("time", 1)

VISION_COMPAT = settings.Get("AR", "vision_compat", True)
TEST_OBJECTS = settings.Get("AR", "test_objects", False)
SHOW_WHEN_NOT_IN_FOCUS = settings.Get("AR", "show_when_not_in_focus", False)

def LoadSettings(data: dict):
    global VISION_COMPAT
    global TEST_OBJECTS
    global SHOW_WHEN_NOT_IN_FOCUS
    VISION_COMPAT = data.get("vision_compat", True)
    TEST_OBJECTS = data.get("test_objects", False)
    SHOW_WHEN_NOT_IN_FOCUS = data.get("show_when_not_in_focus", False)


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

    

def Resize():
    dpg.set_viewport_pos([WindowPosition[0], WindowPosition[1]])
    dpg.set_viewport_width(WindowPosition[2] - WindowPosition[0])
    dpg.set_viewport_height(WindowPosition[3] - WindowPosition[1])


def CalculateAlpha(distances, fade_end=10, fade_start=30, max_fade_start=150, max_fade_end=170, verbose=False):
    if not distances:
        return 0
    
    # Calculate the average distance
    avg_distance = sum(distances) / len(distances)
    
    # Determine the alpha value based on the average distance
    if avg_distance < fade_end:
        return 0
    elif fade_end <= avg_distance < fade_start:
        return (255 * (avg_distance - fade_end) / (fade_start - fade_end))
    elif fade_start <= avg_distance < max_fade_start:
        return 255
    elif max_fade_start <= avg_distance < max_fade_end:
        return (255 * (max_fade_end - avg_distance) / (max_fade_end - max_fade_start))
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


class Settings(ETS2LAPage):
    url = "/settings/AR"
    location = ETS2LAPageLocation.SETTINGS
    title = _("AR")
    refresh_rate = 1

    def vision_compat_changed(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("AR", "vision_compat", True)
        
        settings.Set("AR", "vision_compat", value)
        
    def test_objects_changed(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("AR", "test_objects", False)
        
        settings.Set("AR", "test_objects", value)
        
    def show_when_not_in_focus_changed(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.Get("AR", "show_when_not_in_focus", False)

        settings.Set("AR", "show_when_not_in_focus", value)

    def render(self):
        TitleAndDescription(
            _("AR"),
            _("Change the AR overlay settings here."),
        )
            
        CheckboxWithTitleDescription(
            title=_("Don't hide AR from recording software"),
            description=_("By default the AR overlay is hidden from recording software to prevent it showing up when ETS2LA is using vision systems. If you want to record videos or stream with the overlay, you might want to enable this option."),
            default=settings.Get("AR", "vision_compat", True),
            changed=self.vision_compat_changed,
        )
        
        CheckboxWithTitleDescription(
            title=_("Show test objects"),
            description=_("Show test objects in the AR overlay."),
            default=settings.Get("AR", "test_objects", False),
            changed=self.test_objects_changed,
        )
        
        CheckboxWithTitleDescription(
            title=_("Show when not in focus"),
            description=_("Show the AR overlay even when the game is not in focus. This can be useful for changing settings. Please note that this will also make AR run at the max possible FPS, this might cause some lag."),
            default=settings.Get("AR", "show_when_not_in_focus", False),
            changed=self.show_when_not_in_focus_changed,
        )
        
        try:
            if self.plugin:
                self.refresh_rate = 0.1
                with Container(styles.FlexVertical() + styles.Gap("4px")):
                    UIText(_("Items: {}").format(self.plugin.item_count), styles.Description())
                    UIText(_("Draw Calls: {}").format(self.plugin.draw_calls), styles.Description())
                    UIText(_("Render Time: {:.2f} ms").format(self.plugin.render_time * 1000), styles.Description())
            else:
                self.refresh_rate = 1
        except:
            pass

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name=_("AR"),
        version="1.0",
        description=_("The AR plugin provides an augmented reality overlay for ETS2LA. It used by plugin like HUD to display information in the game world."),
        modules=["TruckSimAPI", "Camera"],
        tags=["Visualization", "AR", "Base"],
        fps_cap=1000
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

    pages = [Settings]

    camera = None
    last_camera_timestamp = 0
    LastTimeStamp = 0

    def imports(self):
        global SCSTelemetry, ScreenCapture, settings, variables, dpg, win32con, win32gui, ctypes, math, time, ttext

        from Modules.TruckSimAPI.main import scsTelemetry as SCSTelemetry
        import Modules.BetterScreenCapture.main as ScreenCapture
        import ETS2LA.Utils.settings as settings
        import ETS2LA.variables as variables

        import dearpygui.dearpygui as dpg
        import Plugins.AR.text as ttext
        
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
        FOV = 75
        
        settings.Listen("AR", LoadSettings)
        InitializeWindow()
        
        renderer = ttext.create_text_renderer()
        self.text_renderer = ttext.TextureText(renderer)
                
        self.draw_calls = 0
        self.render_time = 0
        self.item_count = 0


    def Render(self, items=[]):
        render_start = time.perf_counter()
        self.item_count = len(items)
        
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
        draw_calls = 0
        
        with dpg.viewport_drawlist(label="draw") as FRAME:
            dpg.bind_font(regular_font)
            for i, item in enumerate(sorted_items):
                if type(item) == Rectangle:
                    points = [item.start, item.end]
                    screen_start = points[0].screen(self)
                    screen_end = points[1].screen(self)
                    
                    if screen_start is None or screen_end is None:
                        continue
                    
                    if type(points[0]) == Coordinate:
                        alpha = CalculateAlpha([screen_start[2], screen_end[2]], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        item.color.am = alpha / 255
                        item.fill.am = alpha / 255
                        if item.color.am <= 0 and item.fill.am <= 0:
                            continue
                        
                    elif item.custom_distance:
                        alpha = CalculateAlpha([item.custom_distance], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        item.color.am = alpha / 255
                        item.fill.am = alpha / 255
                        if item.color.am <= 0 and item.fill.am <= 0:
                            continue
                    
                    dpg.draw_rectangle(pmin=screen_start, pmax=screen_end, color=item.color.tuple(), fill=item.fill.tuple(), thickness=item.thickness, rounding=item.rounding)
                    draw_calls += 1
                    
                elif type(item) == Line:
                    points = [item.start, item.end]
                    screen_start = points[0].screen(self)
                    screen_end = points[1].screen(self)
                    
                    if screen_start is None or screen_end is None:
                        continue
                    
                    if type(points[0]) == Coordinate:
                        alpha = CalculateAlpha([screen_start[2], screen_end[2]], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        item.color.am = alpha / 255
                        if item.color.am <= 0:
                            continue
                    
                    dpg.draw_line(p1=screen_start, p2=screen_end, color=item.color.tuple(), thickness=item.thickness)
                    draw_calls += 1
                    
                elif type(item) == Polygon:
                    points = item.points
                    screen_points = [point.screen(self) for point in item.points]
                    
                    if None in screen_points:
                        continue
                    
                    if type(points[0]) == Coordinate:
                        alpha = CalculateAlpha([point[2] for point in screen_points], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        item.color.am = alpha / 255
                        item.fill.am = alpha / 255
                        if item.color.am <= 0 and item.fill.am <= 0:
                            continue
                    
                    dpg.draw_polygon(points=screen_points, color=item.color.tuple(), fill=item.fill.tuple(), thickness=item.thickness)
                    draw_calls += 1
                    
                elif type(item) == Circle:
                    center = item.center
                    screen_center = center.screen(self)
                    
                    if screen_center is None:
                        continue
                    
                    if type(center) == Coordinate:
                        alpha = CalculateAlpha([screen_center[2]], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        item.color.am = alpha / 255
                        item.fill.am = alpha / 255
                        if item.color.am <= 0 and item.fill.am <= 0:
                            continue
                    
                    dpg.draw_circle(center=screen_center, radius=item.radius, color=item.color.tuple(), fill=item.fill.tuple(), thickness=item.thickness)
                    draw_calls += 1
                    
                elif type(item) == Text:
                    position = item.point
                    screen_position = position.screen(self)
                    if screen_position is None:
                        continue
                     
                    if type(position) == Coordinate:
                        alpha = CalculateAlpha([screen_position[2]], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        screen_position = (screen_position[0], screen_position[1])
                        item.color.am = alpha / 255
                        if item.color.am <= 0: 
                            continue
                    
                    elif item.custom_distance:
                        alpha = CalculateAlpha([item.custom_distance], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        item.color.am = alpha / 255
                        if item.color.am <= 0: 
                            continue
                    
                    # Use our texture-based text renderer instead of dpg.draw_text
                    self.text_renderer.draw_text(
                        screen_position,
                        item.text,
                        size=item.size * 0.8,  
                        color=item.color.tuple(),
                        scale=1
                    )
                    draw_calls += 1
                    
                elif type(item) == Bezier:
                    p1 = item.p1.tuple()
                    p2 = item.p2.tuple()
                    p3 = item.p3.tuple()
                    p4 = item.p4.tuple()
                    
                    if item.custom_distance:
                        alpha = CalculateAlpha([item.custom_distance], fade_end=item.fade.prox_fade_end, fade_start=item.fade.prox_fade_start, max_fade_start=item.fade.dist_fade_start, max_fade_end=item.fade.dist_fade_end)
                        item.color.am = alpha / 255
                        if item.color.am <= 0: 
                            continue

                    dpg.draw_bezier_cubic(
                        p1, p2, p3, p4,
                        color=item.color.tuple(),
                        thickness=item.thickness,
                        segments=item.segments,
                    )
                 
        dpg.render_dearpygui_frame()
        self.render_time = time.perf_counter() - render_start
        self.draw_calls = draw_calls

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

        camera = self.modules.Camera.run()
        APIDATA = TruckSimAPI.update()

        HWND = win32gui.FindWindow(None, "ETS2LA AR Overlay")
        if VISION_COMPAT:
            Success = ctypes.windll.user32.SetWindowDisplayAffinity(HWND, 0x00000011)
            if Success == 0:
                print("Failed to hide AR window from screen capture.")
        if not VISION_COMPAT:
            Success = ctypes.windll.user32.SetWindowDisplayAffinity(HWND, 0x00000000)

        # Comment these lines if you want the AR to show up
        # even when the game is paused or not in focus.
        if (APIDATA["pause"] == True or ScreenCapture.IsForegroundWindow(Name="Truck Simulator", Blacklist=["Discord"]) == False) and not SHOW_WHEN_NOT_IN_FOCUS:
            time.sleep(0.1)
            self.Render()
            return
        
        if APIDATA["renderTime"] == self.LastTimeStamp:
            if not SHOW_WHEN_NOT_IN_FOCUS:
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
        
        if camera is not None:
            FOV = camera.fov
            angles = camera.rotation.euler()
            CameraHeadX = camera.position.x + camera.cx * 512
            CameraHeadY = camera.position.y
            CameraHeadZ = camera.position.z + camera.cz * 512

            # We can use the old camera rotation and position if we are in the inside
            # camera view.
            if abs(CameraHeadX - InsideHeadX) > 3 or abs(CameraHeadY - InsideHeadY) > 1 or abs(CameraHeadZ - InsideHeadZ) > 3:
                HeadRotationDegreesX = angles[1]
                HeadRotationDegreesY = angles[0]
                HeadRotationDegreesZ = angles[2]
                HeadX = CameraHeadX
                HeadY = CameraHeadY
                HeadZ = CameraHeadZ
            else:
                HeadX = InsideHeadX
                HeadY = InsideHeadY
                HeadZ = InsideHeadZ
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


        if TEST_OBJECTS:
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
            
            cur = time.time() % 2
            position = Point(100 + cur * 10, 100 + cur * 10)
            DRAWLIST.append(Text(
                position,
                "Testing text smoothness",
                size=64
            ))

        other_plugins = self.globals.tags.AR
        if other_plugins is not None:
            for plugin in other_plugins:
                if type(other_plugins[plugin]) == list:
                    DRAWLIST.extend(other_plugins[plugin])
                    
        other_plugins = self.get_mem_tag("ARraw")
        if other_plugins is not None:
            for plugin in other_plugins:
                # if type(other_plugins[plugin]) == list:
                #     DRAWLIST.extend(other_plugins[plugin])
                if type(other_plugins[plugin]) == list:
                    for item in other_plugins[plugin]:
                        object = get_object_from_dict(item)
                        if object is not None:
                            DRAWLIST.append(object)
        
        self.Render(items=DRAWLIST)
        DRAWLIST = []
