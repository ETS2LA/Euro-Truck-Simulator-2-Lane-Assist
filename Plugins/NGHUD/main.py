# Framework
from Plugins.NGHUD.classes import ElementRunner
from ETS2LA.Utils import settings
from Plugins.AR.classes import *
from Plugins.NGHUD.ui import UI
from ETS2LA.Events import *
from ETS2LA.Plugin import *
import random
import time
import os

def in_out(t, minimum, maximum):
    """Ease in and out function."""
    t = max(0, min(1, t))
    return minimum + (maximum - minimum) * (t * t * (3 - 2 * t))

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="NGHUD",
        version="1.0",
        description="Next-Gen HUD (basically I'm remaking HUD and needed a name for it)",
        modules=["TruckSimAPI", "Semaphores", "Traffic"],
        tags=["Base"],
        listen=["*.py"],
        fps_cap=60 
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )

    pages = [UI]
    runners = []
    
    data = []
    
    renderers = []
    widgets = {
        "Left": None,
        "Center": None,
        "Right": None,
    }

    def discover_elements(self):
        path = "Plugins/NGHUD/elements"
        for filename in os.listdir(path):
            if filename.endswith(".py") and not filename.startswith("__"):
                name = filename[:-3]
                try:
                    runner = ElementRunner(self, name)
                    if runner.element:
                        self.runners.append(runner)
                except Exception as e:
                    print(f"Error loading element {name}: {e}")
                    
        logging.warning(f"NGHUD: Found {len(self.runners)} elements in {path}.")

    def set_widget(self, position: str, name: str):
        if position not in self.widgets:
            raise ValueError(f"Invalid position: {position}. Valid positions are: {list(self.widgets.keys())}")
        
        if self.widgets[position] is not None:
            self.widgets[position].enabled = False
            
        target_widget = next((runner for runner in self.runners if runner.element.name == name), None)
        if target_widget is None:
            raise ValueError(f"Element '{name}' not found in runners.")
        
        self.widgets[position] = target_widget 
        self.widgets[position].enabled = True

    def remove_widget(self, position: str):
        if position not in self.widgets:
            raise ValueError(f"Invalid position: {position}. Valid positions are: {list(self.widgets.keys())}")
        
        if self.widgets[position] is not None:
            self.widgets[position].enabled = False
            self.widgets[position] = None
        else:
            logging.warning(f"NGHUD: No widget to remove at position '{position}'.")

    def enable_renderer(self, name: str):
        target_renderer = next((runner for runner in self.runners if runner.element.name == name), None)
        if target_renderer is None:
            raise ValueError(f"Renderer '{name}' not found in runners.")
         
        target_renderer.enabled = True
        self.renderers.append(target_renderer.element)
        
    def disable_renderer(self, name: str):
        target_renderer = next((runner for runner in self.renderers if runner.name == name), None)
        if target_renderer is None:
            raise ValueError(f"Renderer '{name}' not found in renderers.")
        
        target_renderer.enabled = False
        self.renderers.remove(target_renderer)

    def init(self):
        self.anchor = Coordinate(0, 0, 0, relative=True, rotation_relative=True)
        self.discover_elements()
        self.update_anchor()
        self.get_load_time()
    
    offsets = { # Calculated at runtime
        "Left": 0,
        "Center": 0,
        "Right": 0,
    }

    def get_offset_width_for(self, position:str):
        """Get the offset and width for a given position."""
        if position not in self.widths:
            raise ValueError(f"Invalid position: {position}. Valid positions are: {list(self.widths.keys())}")
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
        
        cabin_offset_x = self.data["headPlacement"]["cabinOffsetX"] + self.data["configVector"]["cabinPositionX"]
        cabin_offset_y = self.data["headPlacement"]["cabinOffsetY"] + self.data["configVector"]["cabinPositionY"]
        cabin_offset_z = self.data["headPlacement"]["cabinOffsetZ"] + self.data["configVector"]["cabinPositionZ"]
        
        head_offset_x = self.data["headPlacement"]["headOffsetX"] + self.data["configVector"]["headPositionX"] + cabin_offset_x
        head_offset_y = self.data["headPlacement"]["headOffsetY"] + self.data["configVector"]["headPositionY"] + cabin_offset_y
        head_offset_z = self.data["headPlacement"]["headOffsetZ"] + self.data["configVector"]["headPositionZ"] + cabin_offset_z
        
        # Get the accurate head position
        head_x = head_offset_x * math.cos(truck_rotation_x) - head_offset_z * math.sin(truck_rotation_x) + truck_x
        head_y = head_offset_y + truck_y
        head_z = head_offset_x * math.sin(truck_rotation_x) + head_offset_z * math.cos(truck_rotation_x) + truck_z
        
        # Now we have
        new_x = coordinate.x - head_x
        new_y = coordinate.y - head_y
        new_z = coordinate.z - head_z
        
        # Rotate these coordinates around the truck rotation Y vector
        new_x_rotated = new_x * math.cos(truck_rotation_x) + new_z * math.sin(truck_rotation_x)
        new_z_rotated = new_z * math.cos(truck_rotation_x) - new_x * math.sin(truck_rotation_x)
        
        new_y_rotated = new_y * math.cos(truck_rotation_y) - new_z_rotated * math.sin(truck_rotation_y)
        new_z_rotated = new_z_rotated * math.cos(truck_rotation_y) + new_y * math.sin(truck_rotation_y)

        return Coordinate(
            new_x_rotated,
            new_y_rotated,
            new_z_rotated,
            relative=True,
            rotation_relative=True 
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
            
        self.anchor = Coordinate(0 + offset_x, -2 + offset_y, -10 + offset_z, relative=True, rotation_relative=True)
        
    def layout(self):
        self.left_width = self.settings.left_width
        if self.left_width is None:
            self.settings.left_width = 100
            self.left_width = 100
            
        self.center_width = self.settings.center_width
        if self.center_width is None:
            self.settings.center_width = 120
            self.center_width = 120
            
        self.right_width = self.settings.right_width
        if self.right_width is None:
            self.settings.right_width = 100
            self.right_width = 100

        padding = 20
        count = 3
        if not self.widgets["Center"] or self.widgets["Center"].data == []:
            self.center_width = 0
            count -= 1
        if not self.widgets["Left"] or self.widgets["Left"].data == []:
            self.left_width = 0
            count -= 1
        if not self.widgets["Right"] or self.widgets["Right"].data == []: 
            self.right_width = 0
            count -= 1
        
        self.total_width = self.left_width + self.center_width + self.right_width + padding * (count - 1)
        self.middle_pixels = self.total_width // 2 
        
        current = 0
        values = [
            [self.left_width, -self.middle_pixels],
            [self.center_width, -self.middle_pixels + self.left_width + padding],
            [self.right_width, -self.middle_pixels + self.left_width + self.center_width + padding * 2]
        ]
        
        if self.widgets["Left"]:
            self.widgets["Left"].width = values[0][0]
            self.widgets["Left"].offset_x = values[current][1]
            current += 1
        
        if self.widgets["Center"]:
            self.widgets["Center"].width = values[1][0]
            self.widgets["Center"].offset_x = values[current][1]
            current += 1

        if self.widgets["Right"]:
            self.widgets["Right"].width = values[2][0]
            self.widgets["Right"].offset_x = values[current][1]
            current += 1

    def ensure_widgets_selected(self):
        left_widget = self.settings.left_widget
        if left_widget is None:
            self.settings.left_widget = "Speed"
            left_widget = "Speed"
            
        center_widget = self.settings.center_widget
        if center_widget is None:
            self.settings.center_widget = "Assist Information"
            center_widget = "Assist Information"
            
        right_widget = self.settings.right_widget
        if right_widget is None:
            self.settings.right_widget = "Media"
            right_widget = "Media"
            
        if not left_widget and self.widgets["Left"] is not None:
            self.remove_widget("Left")
        if left_widget and (self.widgets["Left"] is None or self.widgets["Left"].element.name != left_widget):
            self.set_widget("Left", left_widget)
        
        if not center_widget and self.widgets["Center"] is not None:
            self.remove_widget("Center")
        if center_widget and (self.widgets["Center"] is None or self.widgets["Center"].element.name != center_widget):
            self.set_widget("Center", center_widget)
            
        if not right_widget and self.widgets["Right"] is not None:
            self.remove_widget("Right")
        if right_widget and (self.widgets["Right"] is None or self.widgets["Right"].element.name != right_widget):
            self.set_widget("Right", right_widget) 
            
    def ensure_renderers_selected(self):
        renderers = self.settings.renderers
        if renderers is None:
            self.settings.renderers = ["ACC Information", "Traffic Lights", "Steering Line"]
            renderers = ["ACC Information", "Traffic Lights", "Steering Line"]
            
        enabled = [runner.name for runner in self.renderers]
        for renderer in enabled:
            if renderer not in renderers:
                self.disable_renderer(renderer)
                
        for renderer in renderers:
            if renderer not in enabled:
                self.enable_renderer(renderer)
        
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
            
        return Rectangle(
            Point(-self.middle_pixels - 10, -10, anchor=self.anchor),
            Point(-self.middle_pixels + self.total_width + 10, 60, anchor=self.anchor),
            color=Color(0, 0, 0, 0),
            fill=Color(0, 0, 0, 255 * (darkness if not self.is_day() else day_darkness)),
            rounding=12
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
        t = (time.time() - self.load_start_time) / (self.load_end_time - self.load_start_time)
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
                    fill=Color(0, 0, 0, 255 * (darkness if not self.is_day() else day_darkness)),
                    rounding=12
                ),
                    Rectangle(
                    Point(offset_x, 0, anchor=self.anchor),
                    Point(offset_x + width, height, anchor=self.anchor),
                    color=Color(255, 255, 255, 20 * (1 - max((t - 0.5), 0))),
                    fill=Color(255, 255, 255, 10 * (1 - max((t - 0.5), 0))),
                    rounding=6
                ),
                # Text
                Text(
                    Point(10 + offset_x, 8, anchor=self.anchor),
                    text="ETS2LA",
                    color=Color(255, 255, 255, 200 * (1 - t)),
                    size=16
                ),
                Text(
                    Point(10 + offset_x, height-22, anchor=self.anchor),
                    text=f"Loading...",
                    color=Color(255, 255, 255, 200 * (1 - t)),
                    size=14
                )
            ]
            self.globals.tags.AR = data
            return True
        
        data = [
            Rectangle(
                Point(offset_x - 10, -10, anchor=self.anchor),
                Point(offset_x + width + 10, height + 10, anchor=self.anchor),
                color=Color(0, 0, 0, 0),
                fill=Color(0, 0, 0, 255 * (darkness if not self.is_day() else day_darkness)),
                rounding=12
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
                rounding=6
            ),
            # Progress bar
            Rectangle(
                Point(offset_x, 0, anchor=self.anchor),
                Point(offset_x + width * t, height, anchor=self.anchor),
                color=Color(255, 255, 255, 20),
                fill=Color(255, 255, 255, 10),
                rounding=6
            ),
            # Text
            Text(
                Point(10 + offset_x, 8, anchor=self.anchor),
                text="ETS2LA",
                color=Color(255, 255, 255, 200),
                size=16
            ),
            Text(
                Point(10 + offset_x, height-22, anchor=self.anchor),
                text=f"Loading...",
                color=Color(255, 255, 255, 200),
                size=14
            )
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
        
        self.layout()
        self.ensure_widgets_selected()
        self.ensure_renderers_selected() 
        
        if self.boot_sequence():
            return
        
        data = [self.background()]
        if self.widgets["Left"]: data.extend(self.widgets["Left"].data)
        if self.widgets["Center"]: data.extend(self.widgets["Center"].data)
        if self.widgets["Right"]: data.extend(self.widgets["Right"].data) 
        
        for renderer in self.renderers:
            data += renderer.data
            
        self.globals.tags.AR = data