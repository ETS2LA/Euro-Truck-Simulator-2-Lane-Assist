# Framework
from Plugins.AR.classes import Rectangle, Point, Color, Text, Coordinate
from ETS2LA.Plugin import ETS2LAPlugin, PluginDescription, Author
from Plugins.HUD.classes import ElementRunner
from ETS2LA.Utils.translator import _
from Plugins.HUD.ui import UI
import logging
import random
import math
import time
import os


def in_out(t, minimum, maximum):
    """Ease in and out function."""
    t = max(0, min(1, t))
    return minimum + (maximum - minimum) * (t * t * (3 - 2 * t))


class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name=_("HUD"),
        version="2.0",
        description=_(
            "Creates a heads up display on the windshield. Needs the AR plugin to work."
        ),
        modules=["TruckSimAPI", "Semaphores", "Traffic"],
        tags=["Base"],
        listen=["*.py"],
        fps_cap=60,
    )

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4",
    )

    pages = [UI]
    runners = []

    data = []

    renderers = []
    widgets = []
    default_widgets = [_("Speed"), _("Media"), _("RPM & Gear")]
    widget_sizes = {
        _("Assist Information"): {"width": 120},
        _("Media"): {"width": 160},
        _("Closest City"): {"width": 120},
    }

    widget_scaling = 1.0

    def discover_elements(self):
        path = "Plugins/HUD/elements"
        for filename in os.listdir(path):
            if filename.endswith(".py") and not filename.startswith("__"):
                name = filename[:-3]
                try:
                    runner = ElementRunner(self, name)
                    if runner.element:
                        self.runners.append(runner)
                except Exception as e:
                    print(f"Error loading element {name}: {e}")

        logging.warning(f"HUD: Found {len(self.runners)} elements in {path}.")

    def set_widget(self, name: str):
        target_widget = next(
            (runner for runner in self.runners if runner.element.name == name), None
        )
        if target_widget is None:
            raise ValueError(f"Element '{name}' not found in runners.")

        self.widgets.append(target_widget)
        target_widget.enabled = True

    def remove_widget(self, name: str):
        for widget in self.widgets:
            if widget.element.name == name:
                widget.enabled = False
                self.widgets.remove(widget)
                return

    def enable_renderer(self, name: str):
        target_renderer = next(
            (runner for runner in self.runners if runner.element.name == name), None
        )
        if target_renderer is None:
            raise ValueError(f"Renderer '{name}' not found in runners.")

        target_renderer.enabled = True
        self.renderers.append(target_renderer.element)

    def disable_renderer(self, name: str):
        target_renderer = next(
            (runner for runner in self.renderers if runner.name == name), None
        )
        if target_renderer is None:
            raise ValueError(f"Renderer '{name}' not found in renderers.")

        target_renderer.enabled = False
        self.renderers.remove(target_renderer)

    def init(self):
        self.anchor = Coordinate(0, 0, 0, relative=True, rotation_relative=True)
        self.discover_elements()
        self.update_anchor()
        self.get_load_time()

        scaling = self.settings.get("widget_scaling", 1.0)
        if scaling is None:
            self.settings.widget_scaling = 1.0
            scaling = 1.0

        self.widget_scaling = scaling

    offsets = {  # Calculated at runtime
        "Left": 0,
        "Center": 0,
        "Right": 0,
    }

    def get_offset_width_for(self, position: str):
        """Get the offset and width for a given position."""
        if position not in self.widths:
            raise ValueError(
                f"Invalid position: {position}. Valid positions are: {list(self.widths.keys())}"
            )
        return self.offsets[position], self.widths[position]

    def get_relative_to_head(self, coordinate: Coordinate):
        """Convert a coordinate to be relative to the head position."""
        if not self.data:
            return coordinate

        truck_x = self.data["truckPlacement"]["coordinateX"]
        truck_y = self.data["truckPlacement"]["coordinateY"]
        truck_z = self.data["truckPlacement"]["coordinateZ"]

        truck_rotation_x = self.data["truckPlacement"]["rotationX"]
        truck_rotation_x = -math.radians(truck_rotation_x * 360)

        truck_rotation_y = self.data["truckPlacement"]["rotationY"]
        truck_rotation_y = -math.radians(truck_rotation_y * 360)

        cabin_offset_x = (
            self.data["headPlacement"]["cabinOffsetX"]
            + self.data["configVector"]["cabinPositionX"]
        )
        cabin_offset_y = (
            self.data["headPlacement"]["cabinOffsetY"]
            + self.data["configVector"]["cabinPositionY"]
        )
        cabin_offset_z = (
            self.data["headPlacement"]["cabinOffsetZ"]
            + self.data["configVector"]["cabinPositionZ"]
        )

        head_offset_x = (
            self.data["headPlacement"]["headOffsetX"]
            + self.data["configVector"]["headPositionX"]
            + cabin_offset_x
        )
        head_offset_y = (
            self.data["headPlacement"]["headOffsetY"]
            + self.data["configVector"]["headPositionY"]
            + cabin_offset_y
        )
        head_offset_z = (
            self.data["headPlacement"]["headOffsetZ"]
            + self.data["configVector"]["headPositionZ"]
            + cabin_offset_z
        )

        # Get the accurate head position
        head_x = (
            head_offset_x * math.cos(truck_rotation_x)
            - head_offset_z * math.sin(truck_rotation_x)
            + truck_x
        )
        head_y = head_offset_y + truck_y
        head_z = (
            head_offset_x * math.sin(truck_rotation_x)
            + head_offset_z * math.cos(truck_rotation_x)
            + truck_z
        )

        # Now we have
        new_x = coordinate.x - head_x
        new_y = coordinate.y - head_y
        new_z = coordinate.z - head_z

        # Rotate these coordinates around the truck rotation Y vector
        new_x_rotated = new_x * math.cos(truck_rotation_x) + new_z * math.sin(
            truck_rotation_x
        )
        new_z_rotated = new_z * math.cos(truck_rotation_x) - new_x * math.sin(
            truck_rotation_x
        )

        new_y_rotated = new_y * math.cos(truck_rotation_y) - new_z_rotated * math.sin(
            truck_rotation_y
        )
        new_z_rotated = new_z_rotated * math.cos(truck_rotation_y) + new_y * math.sin(
            truck_rotation_y
        )

        return Coordinate(
            new_x_rotated,
            new_y_rotated,
            new_z_rotated,
            relative=True,
            rotation_relative=True,
        )

    def update_anchor(self):
        offset_x = self.settings.offset_x
        if offset_x is None:
            self.settings.offset_x = 0
            offset_x = 0

        offset_y = self.settings.offset_y
        if offset_y is None:
            self.settings.offset_y = 0
            offset_y = 0

        offset_z = self.settings.offset_z
        if offset_z is None:
            self.settings.offset_z = 0
            offset_z = 0

        self.anchor = Coordinate(
            0 + offset_x,
            -2 + offset_y,
            -10 + offset_z,
            relative=True,
            rotation_relative=True,
        )

    def layout(self):
        widgets = self.widgets
        sizes = self.widget_sizes
        total_width = 0
        total_count = 0
        for widget in widgets:
            if widget.data:
                if widget.element.name in sizes:
                    total_width += (
                        sizes[widget.element.name]["width"] * self.widget_scaling
                    )
                    total_count += 1
                else:
                    total_width += 100 * self.widget_scaling
                    total_count += 1

        total_width += (20 * self.widget_scaling) * (total_count - 1)  # add padding
        self.total_width = total_width
        self.middle_pixels = total_width // 2

        # Now assign width and offsets to each widget
        offset_x = -self.middle_pixels
        for widget in widgets:
            widget_width = (
                sizes.get(widget.element.name, {"width": 100})["width"]
                * self.widget_scaling
            )
            widget.offset_x = offset_x
            widget.width = widget_width

            if self.settings.get("scale_height", False):
                widget.height = 50 * self.widget_scaling
            else:
                widget.height = 50

            if widget.data:
                offset_x += (
                    widget_width + 20 * self.widget_scaling
                )  # add padding between widgets

    def ensure_widgets_selected(self):
        enabled = self.settings.get("widgets", self.default_widgets)
        for widget in enabled:
            if widget not in [runner.element.name for runner in self.widgets]:
                try:
                    self.set_widget(widget)
                except Exception:
                    logging.debug(f"HUD: Widget '{widget}' not found in runners.")

        for widget in self.widgets:
            if widget.element.name not in enabled:
                try:
                    self.remove_widget(widget.element.name)
                except Exception:
                    logging.debug(
                        f"HUD: Widget '{widget.element.name}' not found in runners."
                    )

    def ensure_renderers_selected(self):
        renderers = self.settings.renderers
        if renderers is None:
            self.settings.renderers = [
                _("ACC Information"),
                _("Traffic Lights"),
                _("Steering Line"),
            ]
            renderers = [_("ACC Information"), _("Traffic Lights"), _("Steering Line")]

        enabled = [runner.name for runner in self.renderers]
        for renderer in enabled:
            if renderer not in renderers:
                try:
                    self.disable_renderer(renderer)
                except Exception:
                    logging.debug(f"HUD: Renderer '{renderer}' not found in runners.")

        for renderer in renderers:
            if renderer not in enabled:
                try:
                    self.enable_renderer(renderer)
                except Exception:
                    logging.debug(f"HUD: Renderer '{renderer}' not found in runners.")

    def is_day(self) -> bool:
        if not self.data:
            return False

        time = self.data["commonUI"]["timeRdbl"]
        time = time.split(" ")[1].split(":")[0]
        if time.isdigit():
            time = int(time)
            if 6 <= time < 20:
                return True

        return False

    def background(self):
        darkness = self.settings.darkness
        if not darkness:
            self.settings.darkness = 0
            darkness = 0

        day_darkness = self.settings.day_darkness
        if day_darkness is None:
            self.settings.day_darkness = 0.2
            day_darkness = 0.2

        height = 60
        if self.settings.get("scale_height", False):
            height = 60 * self.widget_scaling

        return Rectangle(
            Point(
                -self.middle_pixels - 10 * self.widget_scaling,
                -10 * self.widget_scaling,
                anchor=self.anchor,
            ),
            Point(
                -self.middle_pixels + self.total_width + 10 * self.widget_scaling,
                height,
                anchor=self.anchor,
            ),
            color=Color(0, 0, 0, 0),
            fill=Color(
                0, 0, 0, 255 * (darkness if not self.is_day() else day_darkness)
            ),
            rounding=12,
        )

    load_start_time = 0
    load_end_time = 0

    def get_load_time(self):
        self.load_start_time = time.time()
        load_time = random.uniform(3, 4)  # Simulate a load time between 4 and 6 seconds
        self.load_end_time = self.load_start_time + load_time

    def lerp(self, start: float, end: float, t: float) -> float:
        """Linear interpolation between start and end based on t."""
        return start + (end - start) * t

    def boot_sequence(self) -> bool:
        t = (time.time() - self.load_start_time) / (
            self.load_end_time - self.load_start_time
        )
        if t > 1.4:
            return False

        width = 200
        height = 50
        offset_x = -width // 2

        darkness = self.settings.darkness
        if not darkness:
            self.settings.darkness = 0
            darkness = 0

        day_darkness = self.settings.day_darkness
        if day_darkness is None:
            self.settings.day_darkness = 0.2
            day_darkness = 0.2

        if t > 1:
            t = (t - 1) / 0.4
            t = in_out(t, 0, 1)
            width = self.lerp(width, self.total_width, t)
            offset_x = self.lerp(offset_x, -self.middle_pixels, t)
            data = [
                Rectangle(
                    Point(offset_x - 10, -10, anchor=self.anchor),
                    Point(offset_x + width + 10, height + 10, anchor=self.anchor),
                    color=Color(0, 0, 0, 0),
                    fill=Color(
                        0, 0, 0, 255 * (darkness if not self.is_day() else day_darkness)
                    ),
                    rounding=12,
                ),
                Rectangle(
                    Point(offset_x, 0, anchor=self.anchor),
                    Point(offset_x + width, height, anchor=self.anchor),
                    color=Color(255, 255, 255, 20 * (1 - max((t - 0.5), 0))),
                    fill=Color(255, 255, 255, 10 * (1 - max((t - 0.5), 0))),
                    rounding=6,
                ),
                # Text
                Text(
                    Point(10 + offset_x, 8, anchor=self.anchor),
                    text="ETS2LA",
                    color=Color(255, 255, 255, 200 * (1 - t)),
                    size=16,
                ),
                Text(
                    Point(10 + offset_x, height - 22, anchor=self.anchor),
                    text=_("Loading..."),
                    color=Color(255, 255, 255, 200 * (1 - t)),
                    size=14,
                ),
            ]
            self.globals.tags.AR = data
            return True

        data = [
            Rectangle(
                Point(offset_x - 10, -10, anchor=self.anchor),
                Point(offset_x + width + 10, height + 10, anchor=self.anchor),
                color=Color(0, 0, 0, 0),
                fill=Color(
                    0, 0, 0, 255 * (darkness if not self.is_day() else day_darkness)
                ),
                rounding=12,
            )
        ]

        t = in_out(t, 0, 1)
        data += [
            # Background
            Rectangle(
                Point(offset_x, 0, anchor=self.anchor),
                Point(offset_x + width, height, anchor=self.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            # Progress bar
            Rectangle(
                Point(offset_x, 0, anchor=self.anchor),
                Point(offset_x + width * t, height, anchor=self.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6,
            ),
            # Text
            Text(
                Point(10 + offset_x, 8, anchor=self.anchor),
                text="ETS2LA",
                color=Color(255, 255, 255, 200),
                size=16,
            ),
            Text(
                Point(10 + offset_x, height - 22, anchor=self.anchor),
                text=_("Loading..."),
                color=Color(255, 255, 255, 200),
                size=14,
            ),
        ]

        self.globals.tags.AR = data
        return True

    def run(self):
        self.data = self.modules.TruckSimAPI.run()
        engine = self.data["truckBool"]["engineEnabled"]

        if not engine:
            self.get_load_time()
            self.globals.tags.AR = []
            return

        self.ensure_widgets_selected()
        self.ensure_renderers_selected()
        self.layout()

        # if self.boot_sequence():
        #     return

        data = [self.background()]
        for widget in self.widgets:
            data += widget.data

        for renderer in self.renderers:
            data += renderer.data

        self.globals.tags.AR = data
