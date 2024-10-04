from utils.data_reader import ReadData
from classes import MapData

data: MapData = None

def Init() -> None:
    global data
    data = ReadData()