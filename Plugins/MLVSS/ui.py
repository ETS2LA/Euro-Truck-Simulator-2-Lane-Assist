import Modules.BetterScreenCapture.main as ScreenCapture
import ETS2LA.Utils.settings as settings
import ETS2LA.variables as variables
import SimpleWindow
import threading
import numpy


def initialize():
    X1, Y1, X2, Y2 = ScreenCapture.GetWindowPosition(Name="Truck Simulator", Blacklist=["Discord"])
    game_x, game_y, game_width, game_height = ScreenCapture.GetScreenDimensions(ScreenCapture.GetScreenIndex((X1 + X2) / 2, (Y1 + Y2) / 2))

    window_x = settings.Get("MLVSS", "window_x", round(game_x + game_width / 3))
    window_y = settings.Get("MLVSS", "window_y", round(game_y + game_height - game_height / 4 - 10))
    window_width = settings.Get("MLVSS", "window_width", round(game_width / 3) if game_width != 0 else 640)
    window_height = settings.Get("MLVSS", "window_height", round(game_height / 4) if game_height != 0 else 270)

    if window_x == None or window_x <= -32000: window_x = settings.Set("MLVSS", "window_x", round(game_x + game_width / 3))
    if window_y == None or window_y <= -32000: window_y = settings.Set("MLVSS", "window_y", round(game_y + game_height - game_height / 4 - 10))
    if window_width == None: window_width = settings.Set("MLVSS", "window_width", round(game_width / 3))
    if window_height == None: window_height = settings.Set("MLVSS", "window_height", round(game_height / 4))

    global FRAME
    FRAME = numpy.zeros((window_height, window_width, 3), dtype=numpy.uint8)

    global window
    window = SimpleWindow.Window(name="ML Vision Sensor System",
                                 size=(window_width, window_height),
                                 position=(window_x, window_y),
                                 title_bar_color=(0, 0, 0),
                                 resizable=True,
                                 topmost=True,
                                 foreground=True,
                                 minimized=False,
                                 undestroyable=True,
                                 icon=variables.ICONPATH)

    global window_position
    global window_size
    window_position = window.get_position()
    window_size = window.get_size()

    threading.Thread(target=run_thread, daemon=True).start()


def update():
    global window_position
    global window_size
    global FRAME

    if window_size != window.get_size():
        window_size = window.get_size()
        settings.Set("MLVSS", "window_width", window_size[0])
        settings.Set("MLVSS", "window_height", window_size[1])
        FRAME = numpy.zeros((window_size[1], window_size[0], 3), dtype=numpy.uint8)

    if window_position != window.get_position():
        window_position = window.get_position()
        settings.Set("MLVSS", "window_x", window_position[0])
        settings.Set("MLVSS", "window_y", window_position[1])

    frame = FRAME.copy()
    window.show(frame)


def run_thread():
    while True:
        update()