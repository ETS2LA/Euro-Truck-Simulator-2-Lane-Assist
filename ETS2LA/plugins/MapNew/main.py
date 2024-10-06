# ETS2LA Imports
from utils.prefab_helpers import display_prefab_routes
from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.utils.translator import Translate
import ETS2LA.plugins.MapNew.classes as c
from utils.data_reader import ReadData
import data
import time

runner: PluginRunner = None

def Initialize():
    data.data = ReadData()
    c.data = data.data # set the classes data variable
    count = 0
    total = len(c.data.prefabs)
    for prefab in c.data.prefabs:
        prefab_description = prefab.prefab_description
        prefab_description.build_nav_routes()
        display_prefab_routes(prefab_description)
        print(f"Built nav routes for prefab {count} / {total} ({count / total * 100:.0f}%)            ", end='\r')
        count += 1
        
    
def plugin():
    ...