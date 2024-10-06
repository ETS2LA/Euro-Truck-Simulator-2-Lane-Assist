# ETS2LA Imports
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
    
def plugin():
    ...