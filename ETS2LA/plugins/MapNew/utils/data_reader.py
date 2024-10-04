import utils.data_extractor as data_extractor
import ETS2LA.backend.settings as settings
import ETS2LA.plugins.MapNew.classes as c
import os

DATA_PATH = "ETS2LA/plugins/MapNew/data/data/"

data_extractor.UpdateData(DATA_PATH)

def FindCategoryFilePath(category: str) -> str:
    for file in os.listdir(DATA_PATH):
        if file.endswith(f"{category}.json"):
            return DATA_PATH + file
    return None

def ReadCities() -> list[c.City]:
    path = FindCategoryFilePath("cities")
    if path is None: return []
    cities: list[c.City] = []
    for city in data_extractor.ReadData(path):
        cities.append(c.City(
            city["token"],
            city["name"],
            None, # name_localized
            city["countryToken"],
            city["population"],
            city["x"],
            city["y"],
            city["z"],
            [c.CityArea(
                area["uid"],
                area["x"],
                area["y"],
                area["z"],
                area["sectorX"],
                area["sectorY"],
                area["token"],
                area["hidden"],
                area["width"],
                area["height"],
            ) for area in city["areas"]]
        ))
        
    return cities


# MARK : ReadData()
def ReadData() -> c.MapData:
    data = c.MapData()
    data.cities = ReadCities()
    print(data.cities)