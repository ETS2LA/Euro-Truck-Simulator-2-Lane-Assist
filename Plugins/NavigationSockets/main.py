from ETS2LA.Plugin import *
from ETS2LA.UI import *

from pyproj import CRS, Transformer
import json

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

ETS2_SCALE = 19.083661390678152
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

ETS2_CRS = CRS.from_proj4(ETS2_PROJ)
UK_CRS = CRS.from_proj4(UK_PROJ)

ETS2_TRANSFORM = Transformer.from_proj(ETS2_CRS, CRS("EPSG:4326"))
UK_TRANSFORM = Transformer.from_proj(UK_CRS, CRS("EPSG:4326"))

def ETS2CoordsToWGS84(x, y):
    calais = [-31100, -5500]
    is_uk = x < calais[0] and y < calais[1]
    x -= 16600 # https://github.com/truckermudgeon/maps/blob/main/packages/libs/map/projections.ts#L40
    y -= 4150
    if is_uk:
        x -= 16650
        y -= 2700
    
    coords = [x, -y]
    if is_uk:
        return UK_TRANSFORM.transform(*coords)[::-1]
    return ETS2_TRANSFORM.transform(*coords)[::-1]

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Navigation Sockets",
        version="1.0",
        description="Provides a socket connection to tmudge's navigation map.",
        modules=["TruckSimAPI"],
        tags=["Base", "Visualization", "Frontend"],
        hidden=True
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    fps_cap = 2
    
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
            {"id": 1,"result": {"type": "started"}},
            {"id": 2,"result": {"type": "started"}},
            {"id": 3,"result": {"type": "started"}},
            {"id": 4,"result": {"type": "started"}}
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
        async with websockets.serve(self.server, "localhost", 3000):
            await asyncio.Future()  # run forever

    def run_server_thread(self):
        asyncio.run(self.start())

    def Initialize(self):
        global TruckSimAPI
        global socket
        
        TruckSimAPI = self.modules.TruckSimAPI
        TruckSimAPI.TRAILER = True
        
        socket = threading.Thread(target=self.run_server_thread)
        socket.start()
        
        print("Navigation sockets waiting for client...")

    def run(self):
        data = TruckSimAPI.run()

        position = (data["truckPlacement"]["coordinateX"], data["truckPlacement"]["coordinateZ"])
        rotation = -data["truckPlacement"]["rotationX"] * 360
        
        speed = data["truckFloat"]["speed"] # m/s
        speed_limit = data["truckFloat"]["speedLimit"]
        speed_mph = speed * 2.23694
        speed_limit_kph = round(speed_limit * 3.6)
        
        packets = [
        {
            "id": 2,
            "result": {
                "type": "data",
                "data": {
                    "position": ETS2CoordsToWGS84(*position),
                    "bearing": rotation,
                    "speedMph": speed_mph,
                    "speedLimit": speed_limit_kph
                },
            }
        },
            {
            "id": 4,
            "result": {
                "type": "data",
                "data": {
                    "position": ETS2CoordsToWGS84(*position),
                    "bearing": rotation,
                    "speedMph": speed_mph,
                    "speedLimit": speed_limit_kph
                },
            }
        }]
            
        # Enqueue the message to all connected clients
        for connection in list(self.connected_clients.values()):
            for packet in packets:
                asyncio.run_coroutine_threadsafe(connection.queue.put(json.dumps(packet)), self.loop)