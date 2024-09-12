import ETS2LA.plugins.Map.GameData.nodes as nodes
from rich.progress import Task, Progress
from ETS2LA.variables import PATH
from typing import List
import json
import math

task: Task = None
progress: Progress = None

citiesFilePath = PATH + "ETS2LA/plugins/Map/GameData/data/Cities.json"

class City:
    name: str
    country: str
    x: float
    y: float
    countryId: int
    localizedNames: List[str]
    
    def __init__(self, name, country, x, y, countryId, localizedNames):
        self.name = name
        self.country = country
        self.x = x
        self.y = y
        self.countryId = countryId
        self.localizedNames = localizedNames
        
    def json(self):
        return {
            "Name": self.name,
            "Country": self.country,
            "X": self.x,
            "Y": self.y,
            "CountryId": self.countryId,
            "LocalizedNames": self.localizedNames
        }
        
    def fromJson(self, jsonData):
        self.name = jsonData["Name"]
        self.country = jsonData["Country"]
        self.x = jsonData["X"]
        self.y = jsonData["Y"]
        self.countryId = jsonData["CountryId"]
        self.localizedNames = jsonData["LocalizedNames"]
        return self
    
    
cities: List[City] = []

def LoadCities():
    progress.update(task, description="[green]cities\n[/green][dim]reading JSON...[/dim]")
    
    jsonData = json.load(open(citiesFilePath, encoding="utf-8"))
    citiesInJson = len(jsonData)
    
    progress.update(task, total=citiesInJson, description="[green]cities\n[/green][dim]parsing...[/dim]", completed=0)
    
    for city in jsonData:
        cityObj = City("", "", 0, 0, 0, [])
        cities.append(cityObj.fromJson(city))
        progress.update(task, advance=1)
    
    progress.update(task, description="[green]cities\n[/green][dim]done![/dim]", completed=citiesInJson)
    
    return cities

def GetClosestCity(x, y):
    closestCity = None
    closestDistance = math.inf
    
    for city in cities:
        distance = math.sqrt((city.x - x) ** 2 + (city.y - y) ** 2)
        if distance < closestDistance:
            closestCity = city
            closestDistance = distance
    
    return closestCity