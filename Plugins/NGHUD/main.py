# Framework
from Plugins.NGHUD.classes import ElementRunner
from ETS2LA.Utils import settings
from Plugins.AR.classes import *
from Plugins.NGHUD.ui import UI
from ETS2LA.Events import *
from ETS2LA.Plugin import *
import time
import os

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

    widgets = {
        "Left": None,
        "Center": None,
        "Right": None,
    }
    
    renderers = []

    def init(self):
        self.anchor = Coordinate(0, 0, 0, relative=True, rotation_relative=True)
        self.discover_elements()
        self.update_anchor()
        
        # TODO: Enable elements based on user selection
        for runner in self.runners:
            if runner.element.name != "Navigation":
                runner.enabled = True
            else:
                continue
                
            if runner.element.name == "Speed":
                self.widgets["Left"] = runner
            elif runner.element.name == "Assist Information":
                self.widgets["Center"] = runner
            elif runner.element.name == "Media":
                self.widgets["Right"] = runner
            else:
                self.renderers.append(runner.element)
    
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
        
        total_width = self.left_width + self.center_width + self.right_width + padding * 2
        self.middle_pixels = total_width // 2 
        
        self.widgets["Left"].width = self.left_width
        self.widgets["Center"].width = self.center_width
        self.widgets["Right"].width = self.right_width
        
        self.widgets["Left"].offset_x = -self.middle_pixels
        self.widgets["Center"].offset_x = -self.middle_pixels + self.left_width + padding
        self.widgets["Right"].offset_x = -self.middle_pixels + self.left_width + self.center_width + padding * 2
        
    def run(self):
        self.layout() 
        self.data = self.modules.TruckSimAPI.run()
        
        data = self.widgets["Left"].data \
             + self.widgets["Center"].data \
             + self.widgets["Right"].data 
        
        for renderer in self.renderers:
            data += renderer.data
            
        self.globals.tags.AR = data