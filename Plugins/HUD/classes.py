from ETS2LA.Plugin import ETS2LAPlugin
import threading
import importlib
import time


class HUDWidget:
    plugin: ETS2LAPlugin
    data: list
    fps: int = 2

    name: str
    description: str
    scale: float = 1.0

    def __init__(self, plugin: ETS2LAPlugin):
        self.plugin = plugin
        self.data = []

    def settings(self) -> dict:
        return {}

    def draw(self, offset_x: int, width: int, height: int = 50): ...


class HUDRenderer:
    plugin: ETS2LAPlugin
    data: list
    fps: int = 2

    name: str
    description: str
    scale: float = 1.0

    def __init__(self, plugin: ETS2LAPlugin):
        self.plugin = plugin
        self.data = []

    def settings(self) -> dict:
        return {}

    def draw(self): ...


class ElementRunner:
    element: HUDRenderer | HUDWidget
    plugin: ETS2LAPlugin

    offset_x: int = 0
    width: int = 0
    height: int = 50

    enabled: bool = False
    data: list = []

    def __init__(self, plugin: ETS2LAPlugin, name: str):
        path = f"Plugins.HUD.elements.{name}"
        print(f"Loading HUD element: {path}")
        module = importlib.import_module(path)
        # Try to find "Renderer" or "Widget" class in the module
        try:
            self.element = module.Renderer(plugin)
        except Exception:
            try:
                self.element = module.Widget(plugin)
            except AttributeError as e:
                raise ImportError(
                    f"Element {name} does not have a Renderer or Widget class."
                ) from e

        self.plugin = plugin
        threading.Thread(target=self.run_element, daemon=True).start()

    def run_element(self):
        while True:
            time.sleep(1 / self.element.fps)

            if not self.enabled:
                continue

            self.element.scale = self.plugin.widget_scaling

            if isinstance(self.element, HUDRenderer):
                try:
                    self.element.draw()
                except Exception:
                    self.data = []

            elif isinstance(self.element, HUDWidget):
                try:
                    self.element.draw(self.offset_x, self.width, self.height)
                except Exception:
                    self.data = []

            self.data = self.element.data
