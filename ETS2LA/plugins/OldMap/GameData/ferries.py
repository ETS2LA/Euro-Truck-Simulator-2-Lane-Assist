import ETS2LA.plugins.OldMap.GameData.nodes as nodes
from rich.progress import Task, Progress
from ETS2LA.variables import PATH
from typing import List
import json

task: Task = None
progress: Progress = None

ferryPortFilePath = PATH + "ETS2LA/plugins/Map/GameData/data/ferry_ports.json"
ferryConnectionFilePath = PATH + "ETS2LA/plugins/Map/GameData/data/ferry_connections.json"

class FerryPortLocation:
    IsEmpty: bool = False
    X: float = 0
    Y: float = 0
    
class FerryPortConnection:
    X: float = 0
    Z: float = 0
    Rotation: float = 0
    
class FerryConnection:
    Connections: List[FerryPortConnection] = []
    Price: int = 0
    Time: int = 0
    Distance: int = 0
    StartPortToken: int = 0
    StartPortLocation: FerryPortLocation = None
    EndPortToken: int = 0
    EndPortLocation: FerryPortLocation = None

class FerryPort:    
    StartNodeUid: int = 0
    EndNodeUid: int = 0
    StartNode: nodes.Node = None
    EndNode: nodes.Node = None
    DlcGuard: int = 0
    FerryPortId: int = 0
    Uid: int = 0
    Nodes: List[nodes.Node] = []
    BlockSize: int = 0
    Valid: bool = False
    Type: int = 0
    X: float = 0
    Y: float = 0
    Z: float = 0
    Hidden: bool = False
    Flags: int = 0
    
ports: List[FerryPort] = []
connections: List[FerryConnection] = []
    
def LoadFerries():
    progress.update(task, description="[green]ferries\n[/green][dim]reading JSON...[/dim]")
    
    jsonData = json.load(open(ferryPortFilePath))
    ferriesInJson = len(jsonData)
    
    progress.update(task, total=ferriesInJson, description="[green]ferries\n[/green][dim]parsing...[/dim]", completed=0)
    
    count = 0
    for key in jsonData:
        ferry = jsonData[key]
        ferryObj = FerryPort()
        ferryObj.StartNodeUid = ferry["StartNodeUid"]
        ferryObj.EndNodeUid = ferry["EndNodeUid"]
        ferryObj.StartNode = nodes.GetNodeByUid(ferry["StartNodeUid"]) # always null
        ferryObj.EndNode = nodes.GetNodeByUid(ferry["EndNodeUid"]) # always null
        ferryObj.DlcGuard = ferry["DlcGuard"]
        ferryObj.FerryPortId = ferry["FerryPortId"]
        ferryObj.Uid = ferry["Uid"]
        ferryObj.BlockSize = ferry["BlockSize"]
        ferryObj.Valid = ferry["Valid"]
        ferryObj.Type = ferry["Type"]
        ferryObj.X = ferry["X"]
        ferryObj.Y = ferry["Y"]
        ferryObj.Z = ferry["Z"]
        ferryObj.Hidden = ferry["Hidden"]
        ferryObj.Flags = ferry["Flags"]
        
        ferryObj.Nodes = []
        for node in ferry["Nodes"]:
            ferryObj.Nodes.append(nodes.GetNodeByUid(node))
        
        ports.append(ferryObj)
        
        count += 1
        progress.advance(task)
        
    del jsonData
    
    progress.update(task, description="[green]ferries\n[/green][dim]reading JSON...[/dim]")
    
    jsonData = json.load(open(ferryConnectionFilePath))
    ferriesInJson = len(jsonData)
    
    progress.update(task, total=ferriesInJson, description="[green]ferries\n[/green][dim]parsing...[/dim]", completed=0)
    
    count = 0
    for ferry in jsonData:
        ferryObj = FerryConnection()
        ferryObj.Price = ferry["Price"]
        ferryObj.Time = ferry["Time"]
        ferryObj.Distance = ferry["Distance"]
        
        ferryObj.StartPortToken = ferry["StartPortToken"]
        ferryObj.StartPortLocation = FerryPortLocation()
        ferryObj.StartPortLocation.IsEmpty = ferry["StartPortLocation"]["IsEmpty"]
        ferryObj.StartPortLocation.X = ferry["StartPortLocation"]["X"]
        ferryObj.StartPortLocation.Y = ferry["StartPortLocation"]["Y"]
        
        ferryObj.EndPortToken = ferry["EndPortToken"]
        ferryObj.EndPortLocation = FerryPortLocation()
        ferryObj.EndPortLocation.IsEmpty = ferry["EndPortLocation"]["IsEmpty"]
        ferryObj.EndPortLocation.X = ferry["EndPortLocation"]["X"]
        ferryObj.EndPortLocation.Y = ferry["EndPortLocation"]["Y"]
        
        ferryObj.Connections = []
        for connection in ferry["Connections"]:
            conn = FerryPortConnection()
            conn.X = connection["X"]
            conn.Z = connection["Z"]
            conn.Rotation = connection["Rotation"]
            ferryObj.Connections.append(conn)
        
        connections.append(ferryObj)
        
        count += 1
        progress.advance(task)
        

def FindPortByID(ID: int) -> FerryPort:
    for port in ports:
        if port.FerryPortId == ID:
            return port
    return None

startCache = {
   
}
def FindEndPortByStartUid(start: int) -> List[FerryPort]:
    if start in startCache:
        return startCache[start]
    
    port: FerryPort = None
    for ferry in ports:
        if ferry.Uid == start:
            port = ferry
            break
        
    if port == None:
        return None
    
    id = port.FerryPortId
    connectionsThatStartHere: List[FerryConnection] = []
    for connection in connections:
        if connection.StartPortToken == id:
            connectionsThatStartHere.append(connection)
        
    endPorts = []
    for connection in connectionsThatStartHere:
        for port in ports:
            if port.FerryPortId == connection.EndPortToken:
                endPorts.append(port)
    
    startCache[start] = endPorts
    
    return endPorts

endCache = {
       
}
def FindStartPortByEndUid(end: int) -> List[FerryPort]:
    if end in endCache:
        return endCache[end]
    
    port: FerryPort = None
    for ferry in ports:
        if ferry.Uid == end:
            port = ferry
            break
        
    if port == None:
        return None
    
    id = port.FerryPortId
    connectionsThatEndHere: List[FerryConnection] = []
    for connection in connections:
        if connection.EndPortToken == id:
            connectionsThatEndHere.append(connection)
        
    startPorts = []
    for connection in connectionsThatEndHere:
        for port in ports:
            if port.FerryPortId == connection.StartPortToken:
                startPorts.append(port)
                
    endCache[end] = startPorts
                
    return startPorts