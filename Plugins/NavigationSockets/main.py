from ETS2LA.Plugin import *
from ETS2LA.UI import *

from Plugins.Map.utils.math_helpers import Hermite3D, DistanceBetweenPoints

from pyproj import CRS, Transformer
import json
import math

class WebSocketConnection:
    def __init__(self, websocket):
        self.websocket = websocket
        self.queue = asyncio.Queue()
        self.sender_task = asyncio.create_task(self.send_messages())

    async def send_messages(self):
        try:
            while True:
                message = await self.queue.get()
                await self.websocket.send(message)
        except Exception as e:
            print("Client disconnected due to exception in send_messages.", str(e))

def lengthOfDegreeAt(latInDegrees):
    m1 = 111132.92
    m2 = -559.82
    m3 = 1.175
    m4 = -0.0023

    lat = math.radians(latInDegrees)
    return (
        m1 +
        m2 * math.cos(2 * lat) +
        m3 * math.cos(4 * lat) +
        m4 * math.cos(6 * lat)
    )

#--- Projection Parameters & Transformer Definition ---
#Clarke 1866 Spheroid Radius & Degree Length
EARTH_RADIUS = 6_370_997  # :contentReference[oaicite:8]{index=8}
LENGTH_OF_DEGREE = ((EARTH_RADIUS * math.pi) / 180)  # :contentReference[oaicite:9]{index=9}
ETS2_SCALE = abs(lengthOfDegreeAt(50) * -0.000171570875)
BASE_ETS2 = [ # https://github.com/truckermudgeon/maps/blob/main/packages/libs/map/projections.ts#L46
    "+proj=lcc",
    "+units=m",
    "+ellps=sphere",
    "+lat_1=37",
    "+lat_2=65",
    "+lat_0=50",
    "+lon_0=15"
]

ETS2_PROJ = " ".join([
    *BASE_ETS2,
    f"+k_0={1 / ETS2_SCALE}"
])
UK_PROJ = " ".join([
    *BASE_ETS2,
    f"+k_0={1 / (ETS2_SCALE * 0.75)}",
])
# print(ETS2_PROJ)
ETS2_CRS = CRS.from_proj4(ETS2_PROJ)
UK_CRS = CRS.from_proj4(UK_PROJ)

ETS2_TRANSFORM = Transformer.from_crs(ETS2_CRS, CRS("EPSG:4326"))
UK_TRANSFORM = Transformer.from_crs(UK_CRS, CRS("EPSG:4326"))

# The projection definition for ATS (North America)
ATS_STD_PARALLEL_1 = 33
ATS_STD_PARALLEL_2 = 45
ATS_LAT0 = 39
ATS_LON0 = -96
ATS_MAP_FACTOR = (-0.00017706235, 0.000176689948)  
ATS_SCALE = abs(lengthOfDegreeAt(ATS_LAT0) * ATS_MAP_FACTOR[0])

ATS_PROJ = (
    f"+proj=lcc "
    f"+units=m +R={EARTH_RADIUS} "
    f"+lat_1={ATS_STD_PARALLEL_1} +lat_2={ATS_STD_PARALLEL_2} "
    f"+lat_0={ATS_LAT0} +lon_0={ATS_LON0} " 
    #f"+k_0={1 / ATS_SCALE} "
    #f"+x_0=0 +y_0=-1750 "
    #f"+no_defs"
)
ATS_CRS         = CRS.from_proj4(ATS_PROJ)
ATS_TRANSFORM   = Transformer.from_crs(ATS_CRS, CRS("EPSG:4326"))  

# Threshold for map detection
ATS_X_MIN = -120000
ATS_X_MAX = 20000  
ATS_Y_MIN = -80000     
ATS_Y_MAX = 80000

def CoordsToWGS84(x, y, game="ETS2"):
    """
    Convert game (x, y) coords into WGS84.
    Support both ETS2 (Europe/UK) and ATS (North America) maps.
    """

    if game == "ATS":
        offset_x = round(36 * (1 / (1 + math.exp(0.0001 * (x + 60000)))))
        pos_y_factor = 1 / (1 + math.exp(-0.00015 * (y - 20000)))
        neg_y_factor = 1 / (1 + math.exp(0.00015 * (y + 40000)))
        offset_y = round(45 * pos_y_factor - 108 * neg_y_factor)
        
        x -= offset_x
        y -= offset_y
        proj_x = x * ATS_MAP_FACTOR[1] * LENGTH_OF_DEGREE
        proj_y = y * ATS_MAP_FACTOR[0] * LENGTH_OF_DEGREE
        lon, lat = ATS_TRANSFORM.transform(proj_x, proj_y)
        return (lat, lon)
    
    else: # ETS2
        calais = [-31100, -5500]
        is_uk = x < calais[0] and y < calais[1]
        x -= 16660 # https://github.com/truckermudgeon/maps/blob/main/packages/libs/map/projections.ts#L40
        y -= 4150
        if is_uk:
            x -= 16650
            y -= 2700
        
        coords = [x, -y]
        if is_uk:
            return UK_TRANSFORM.transform(*coords)[::-1]
        
        return ETS2_TRANSFORM.transform(*coords)[::-1]

last_angle = 0
last_position = (0, 0)

def degrees_to_radians(degrees):
    return degrees * math.pi / 180

def radians_to_degrees(radians):
    return radians * 180 / math.pi

# https://github.com/Turfjs/turf/blob/master/packages/turf-bearing/index.ts
def bearing(start, end):
    """
    Calculates the bearing (heading) between two geographic coordinates.
    """
    lon1, lat1 = start
    lon2, lat2 = end
    
    # Convert degrees to radians
    lon1 = degrees_to_radians(lon1)
    lon2 = degrees_to_radians(lon2)
    lat1 = degrees_to_radians(lat1)
    lat2 = degrees_to_radians(lat2)

    a = math.sin(lon2 - lon1) * math.cos(lat2)
    b = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    
    return radians_to_degrees(math.atan2(a, b))

def ConvertAngleToWGS84Heading(position, speed, game="ETS2"):
    global last_position, last_angle

    if position == last_position:
        return last_angle

    last_wgs84 = CoordsToWGS84(*last_position, game=game)
    cur_wgs84 = CoordsToWGS84(*position, game=game)

    geographic_heading = bearing(last_wgs84, cur_wgs84)

    geographic_heading = (geographic_heading + 360) % 360
    
    if speed < 0:
        geographic_heading = (geographic_heading + 180) % 360
    
    last_position = position
    last_angle = geographic_heading

    return geographic_heading

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="plugin.navigationsockets",
        version="1.0",
        description="plugin.navigationsockets.description",
        modules=["TruckSimAPI"],
        tags=["Base", "Visualization", "Frontend"],
        hidden=False,
        fps_cap=2
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    last_navigation_time = 0
    
    def init(self):
        self.connected_clients = {}
        self.loop = None

    def imports(self):
        global multiprocessing, websockets, threading, logging, asyncio, json, os, time
        import multiprocessing
        import websockets
        import threading
        import logging
        import asyncio
        import json
        import time
        import os

    async def server(self, websocket):
        print("Client Connected!")
        connection = WebSocketConnection(websocket)
        self.connected_clients[websocket] = connection
        print("Number of connected clients: ", len(self.connected_clients))
        response = [
            #{"id": 1,"result": {"type": "started"}},
            {"id": 2,"result": {"type": "started"}},
            #{"id": 3,"result": {"type": "started"}},
            {"id": 4,"result": {"type": "started"}},
            {"id": 5,"result": {"type": "started"}},
        ]
        try:
            async for message in websocket:
                print("Received message from client: ", message)
                # Respond to any message with the response
                await websocket.send(json.dumps(response))
                print("Sent response to client.")
                
                
        except Exception as e:
            print("Client disconnected due to exception.", str(e))
        finally:
            connection.sender_task.cancel()
            del self.connected_clients[websocket]
            print("Client disconnected. Number of connected clients: ", len(self.connected_clients))

    async def start(self):
        self.loop = asyncio.get_running_loop()
        async with websockets.serve(self.server, "localhost", 62840):
            await asyncio.Future()  # run forever

    def run_server_thread(self):
        asyncio.run(self.start())

    def Initialize(self):
        global TruckSimAPI
        global socket
        
        TruckSimAPI = self.modules.TruckSimAPI
        TruckSimAPI.TRAILER = True
        
        socket = threading.Thread(target=self.run_server_thread, daemon=True)
        socket.start()
        
        print("Navigation sockets waiting for client...")

    def run(self):
        data = TruckSimAPI.run()

        position = (data["truckPlacement"]["coordinateX"], data["truckPlacement"]["coordinateZ"])
        speed = data["truckFloat"]["speed"] * 1.25 # offset to make it zoom out faster
        game = data["scsValues"]["game"]
        
        if speed > 0.2 or speed < -0.2:
            rotation = ConvertAngleToWGS84Heading(position, speed, game=game)
        else:
            rotation = last_angle
            
        speed_mph = speed * 2.23694
        
        packets = [
        {
            "id": 2,
            "result": {
                "type": "data",
                "data": {
                    "position": CoordsToWGS84(*position, game=game),
                    "bearing": rotation,
                    "speedMph": speed_mph,
                    "speedLimit": 0
                },
            }
        },
        {
            "id": 4,
            "result": {
                "type": "data",
                "data": "dark"
            }
        },
        {
            "id": 5,
            "result": {
                "type": "data",
                "data": {
                    "position": CoordsToWGS84(*position, game=game),
                    "bearing": rotation,
                    "speedMph": speed_mph,
                    "speedLimit": 0
                },
            }
        }]
        
        navigation = self.globals.tags.navigation_plan
        navigation = self.globals.tags.merge(navigation)
        if time.time() - self.last_navigation_time > 10 and navigation is not None and len(navigation) > 0: # Send the navigation plan every 10 seconds
            self.last_navigation_time = time.time()
            
            total_points = []
            for i in range(len(navigation) - 1):
                nav = navigation[i]
                item = nav.item
                
                if not item or not hasattr(item, 'points'):
                    total_points.append([nav.node.x, nav.node.y, nav.node.z])
                    continue
                
                points = item.points
                
                if len(points) < 5:
                    points = [point.tuple() for point in points]
                    points = [(point[0], point[2], point[1]) for point in points]  # Convert to (x, z, y) format
                    continue
                
                # Get 5 equally spaced points
                start_index = 0
                end_index = len(points) - 1
                step = (end_index - start_index) / 4
                new_points = []
                for j in range(5):
                    index = int(start_index + j * step)
                    if index < 0 or index >= len(points):
                        continue
                    point = points[index]
                    point = (point.x, point.z, point.y)
                    new_points.append(point)
                    
                # Check if we need to invert them
                if nav.direction == "backward":
                    new_points.reverse()
                    
                total_points.extend(new_points)
                
            packets.append({
                "id": "1",
                "result": {
                    "type": "data",
                    "data": {
                            "id": "1",
                            "segments": [
                                {
                                    "key": "route",
                                    "lonLats": [CoordsToWGS84(point[0], point[1], game=game) for point in total_points],
                                    "distance": math.sqrt((navigation[-1].node.x - navigation[0].node.x) ** 2 + (navigation[-1].node.y - navigation[0].node.y) ** 2),
                                    "time": 0,
                                    "strategy": "shortest",
                                }
                            ]
                    }
                }       
            })
        
        # Enqueue the message to all connected clients
        for connection in list(self.connected_clients.values()):
            for packet in packets:
                asyncio.run_coroutine_threadsafe(connection.queue.put(json.dumps(packet)), self.loop)
