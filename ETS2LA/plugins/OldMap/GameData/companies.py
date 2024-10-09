from ETS2LA.plugins.OldMap.GameData.cities import City, GetClosestCity
import ETS2LA.plugins.OldMap.GameData.nodes as nodes
from rich.progress import Task, Progress
from ETS2LA.variables import PATH
from typing import List
import json
import math

task: Task = None
progress: Progress = None

companyFilePath = PATH + "ETS2LA/plugins/Map/GameData/data/Overlays.json"

class Company:
    x: float
    y: float
    name: str
    closestCity: City
    
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        
    def json(self):
        return {
            "X": self.x,
            "Y": self.y,
            "Name": self.name
        }
        
    def fromJson(self, jsonData):
        self.x = jsonData["X"]
        self.y = jsonData["Y"]
        self.name = jsonData["Name"]
        return self
    
    
companies: List[Company] = []

def LoadCompanies():
    progress.update(task, description="[green]companies\n[/green][dim]reading JSON...[/dim]")
    
    jsonData = json.load(open(companyFilePath, encoding="utf-8"))
    companiesInJson = len(jsonData)
    
    progress.update(task, total=companiesInJson, description="[green]companies\n[/green][dim]parsing...[/dim]", completed=0)
    
    for overlay in jsonData:
        if overlay["Type"] != "Company":
            continue
        
        companyObj = Company(0, 0, "")
        companyObj.fromJson(overlay)
        companies.append(companyObj)
        
        progress.update(task, advance=1)
        
    progress.update(task, description="[green]companies\n[/green][dim]finding closest cities...[/dim]")
        
    for company in companies:
        company.closestCity = GetClosestCity(company.x, company.y)
        progress.update(task, advance=1)
        

def GetClosestCompany(x, y):
    closestCompany = None
    closestDistance = math.inf
    
    for company in companies:
        distance = math.sqrt((company.x - x) ** 2 + (company.y - y) ** 2)
        if distance < closestDistance:
            closestDistance = distance
            closestCompany = company
            
    return closestCompany

def GetCompaniesByName(name):
    return [company for company in companies if company.name == name]

def GetCompaniesByCity(city):
    return [company for company in companies if company.closestCity == city]

def GetCompanyInCity(name, city):
    return [company for company in companies if company.name == name and company.closestCity.name == city]