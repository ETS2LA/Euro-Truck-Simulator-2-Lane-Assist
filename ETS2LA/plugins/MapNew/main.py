# ETS2LA Imports
from ETS2LA.plugins.runner import PluginRunner
from ETS2LA.utils.translator import Translate
import time
import data

runner: PluginRunner = None

def Initialize():
    ...
    data.Init()
    
def plugin():
    ...