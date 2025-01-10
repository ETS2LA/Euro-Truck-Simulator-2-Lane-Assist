import Modules.BetterScreenCapture.main as ScreenCapture
import ETS2LA.Utils.settings as Settings
import ETS2LA.variables as Variables
import SimpleWindow
import threading
import numpy




def Initialize():
    X1, Y1, X2, Y2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
    GameX, GameY, GameWidth, GameHeight = ScreenCapture.GetScreenDimensions(ScreenCapture.GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2))

    WindowX = Settings.Get("MLVSS", "WindowX", round(GameX + GameWidth / 3))
    WindowY = Settings.Get("MLVSS", "WindowY", round(GameY + GameHeight - GameHeight / 4 - 10))
    WindowWidth = Settings.Get("MLVSS", "WindowWidth", round(GameWidth / 3))
    WindowHeight = Settings.Get("MLVSS", "WindowHeight", round(GameHeight / 4))

    if WindowX == None or WindowX <= -32000: WindowX = Settings.Set("MLVSS", "WindowX", round(GameX + GameWidth / 3))
    if WindowY == None or WindowY <= -32000: WindowY = Settings.Set("MLVSS", "WindowY", round(GameY + GameHeight - GameHeight / 4 - 10))
    if WindowWidth == None: WindowWidth = Settings.Set("MLVSS", "WindowWidth", round(GameWidth / 3))
    if WindowHeight == None: WindowHeight = Settings.Set("MLVSS", "WindowHeight", round(GameHeight / 4))

    global FRAME
    FRAME = numpy.zeros((WindowHeight, WindowWidth, 3), dtype=numpy.uint8)

    SimpleWindow.Initialize(Name="ML Vision Sensor System",
                            Size=(WindowWidth, WindowHeight),
                            Position=(WindowX, WindowY),
                            TitleBarColor=(0, 0, 0),
                            Resizable=True,
                            TopMost=True,
                            Foreground=True,
                            Minimized=False,
                            Undestroyable=True,
                            Icon=f"{Variables.PATH}ETS2LA/Window/favicon.ico")

    global WindowPosition
    global WindowSize
    WindowPosition = SimpleWindow.GetPosition("ML Vision Sensor System")
    WindowSize = SimpleWindow.GetSize("ML Vision Sensor System")

    threading.Thread(target=RunThread, daemon=True).start()


def Update():
    global WindowPosition
    global WindowSize
    global FRAME

    if WindowSize != SimpleWindow.GetSize("ML Vision Sensor System"):
        WindowSize = SimpleWindow.GetSize("ML Vision Sensor System")
        Settings.Set("MLVSS", "WindowWidth", WindowSize[0])
        Settings.Set("MLVSS", "WindowHeight", WindowSize[1])
        FRAME = numpy.zeros((WindowSize[1], WindowSize[0], 3), dtype=numpy.uint8)

    if WindowPosition != SimpleWindow.GetPosition("ML Vision Sensor System"):
        WindowPosition = SimpleWindow.GetPosition("ML Vision Sensor System")
        Settings.Set("MLVSS", "WindowX", WindowPosition[0])
        Settings.Set("MLVSS", "WindowY", WindowPosition[1])

    Frame = FRAME.copy()
    SimpleWindow.Show("ML Vision Sensor System", Frame)


def RunThread():
    while True:
        Update()