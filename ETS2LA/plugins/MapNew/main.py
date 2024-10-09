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
import route.planning as planning
import route.driving as driving

# General imports
import data
import time
import math

api = None
steering = None
runner: PluginRunner = None

INTERNAL_MAP = True
MAP_INITIALIZED = False

def ToggleSteering(state:bool, *args, **kwargs):
    data.enabled = state

def Initialize():
    global api
    global steering
    
    data.runner = runner
    data.controller = runner.modules.SDKController.SCSController()
    data.map = ReadData()
    c.data = data # set the classes data variable
    api = runner.modules.TruckSimAPI
    
    steering = runner.modules.Steering
    steering.OFFSET = 0
    steering.SMOOTH_TIME = 0.2
    steering.IGNORE_SMOOTH = False
    steering.SENSITIVITY = 1
    
    
def plugin():
    global MAP_INITIALIZED
    
    api_data = api.run()
    data.UpdateData(api_data)
    runner.Profile("Main - API")
    planning.UpdateRoutePlan()
    runner.Profile("Main - Route Plan")
    steering_value = driving.GetSteering()
    steering.run(value=steering_value/180, sendToGame=data.enabled, drawLine=False)
    runner.Profile("Steering - Send to game")
    
    if not MAP_INITIALIZED and INTERNAL_MAP:
        im.InitializeMapWindow()
        MAP_INITIALIZED = True
        
    if MAP_INITIALIZED and not INTERNAL_MAP:
        im.RemoveWindow()
        MAP_INITIALIZED = False
    
    if INTERNAL_MAP:
        im.DrawMap(runner)
        
    runner.Profile("Map")