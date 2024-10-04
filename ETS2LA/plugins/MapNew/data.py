from utils.data_reader import ReadData
from classes import MapData

data: MapData = None
"""This includes all of the ETS2 data that can be accessed."""

def Init() -> None:
    global data
    data = ReadData()