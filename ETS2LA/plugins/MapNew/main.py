# Imports to fix circular imports
import utils.prefab_helpers as ph
import utils.road_helpers as rh
import utils.math_helpers as mh
import utils.internal_map as im

# ETS2LA imports
from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.utils.translator import Translate
import ETS2LA.plugins.MapNew.classes as c
from utils.data_reader import ReadData

# General imports
import data
import time
import math

api = None
runner: PluginRunner = None

INTERNAL_MAP = True
MAP_INITIALIZED = False

def Initialize():
    global api
    data.data = ReadData()
    c.data = data # set the classes data variable
    api = runner.modules.TruckSimAPI
        
def UpdateData(api_data):
    data.heavy_calculations_this_frame = 0
    
    data.truck_x = api_data["truckPlacement"]["coordinateX"]
    data.truck_y = api_data["truckPlacement"]["coordinateY"]
    data.truck_z = api_data["truckPlacement"]["coordinateZ"]
    
    data.current_sector_x, data.current_sector_y = data.data.get_sector_from_coordinates(data.truck_x, data.truck_z)
    
    data.current_sector_prefabs = data.data.get_sector_prefabs_by_sector([data.current_sector_x, data.current_sector_y])
    data.current_sector_roads = data.data.get_sector_roads_by_sector([data.current_sector_x, data.current_sector_y])
    
    rotationX = api_data["truckPlacement"]["rotationX"]
    angle = rotationX * 360
    if angle < 0: angle = 360 + angle
    data.truck_rotation = -math.radians(angle)
    
def plugin():
    global MAP_INITIALIZED
    
    api_data = api.run()
    UpdateData(api_data)
    
    if not MAP_INITIALIZED and INTERNAL_MAP:
        im.InitializeMapWindow()
        MAP_INITIALIZED = True
        
    if MAP_INITIALIZED and not INTERNAL_MAP:
        im.RemoveWindow()
        MAP_INITIALIZED = False
    
    if INTERNAL_MAP:
        im.DrawMap()