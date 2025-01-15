"""
Communication interface docs:

base_url: ws://localhost:37522
client_base_message: 
{
    "method": string, # Method type (subscribe, unsubscribe, query etc...)
    "channel": number, # 0 is reserved for messages to the backend
    "params": {
        "name": string, # Method name (available_channels, available_methods etc...)
    }
}
server_base_message:
{
    "channel": number,
    "result": {
        "type": string, # Response type (data)
        "data": {
            ...
        }
    }
}

To start off call the server with the following after connecting:
{
    "method": "query",
    "channel": 0,
    "params": {
        "name": "available_channels"
    }
}
"""

import multiprocessing
import websockets
import threading
import logging
import asyncio
import json
import time
import os
        
from ETS2LA.Plugin import *
from ETS2LA.UI import *

available_channels = [
    {
        "channel": 0,
        "name": "Handshake",
        "description": "Reserved for initial handshake and connection setup.",
        "commands": [
            {
                "name": "available_channels",
                "method": "query",
                "description": "Returns a list of available channels and their descriptions."
            }
        ]
    },
    {
        "channel": 1,
        "name": "Transform",
        "description": "Current truck position and orientation in the game world.",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the truck position and orientation updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the truck position and orientation updates."
            }
        ]
    }
]

class WebSocketConnection:
    def __init__(self, websocket):
        self.websocket = websocket
        self.queue = asyncio.Queue()
        self.sender_task = asyncio.create_task(self.send_messages())
        self.subscribed_channels = set()

    async def send_messages(self):
        try:
            while True:
                message = await self.queue.get()
                await self.websocket.send(message)
        except Exception as e:
            print("Client disconnected due to exception in send_messages.", str(e))

"""
Communication interface docs:

base_url: ws://localhost:37522
client_base_message: 
{
    "method": string, # Method type (subscribe, unsubscribe, query etc...)
    "channel": number, # 0 is reserved for messages to the backend
    "params": {
        "name": string, # Method name (available_channels, available_methods etc...)
    }
}
server_base_message:
{
    "channel": number,
    "result": {
        "type": string, # Response type (data)
        "data": {
            ...
        }
    }
}

To start off call the server with the following after connecting:
{
    "method": "query",
    "channel": 0,
    "params": {
        "name": "available_channels"
    }
}
"""

import multiprocessing
import websockets
import threading
import logging
import asyncio
import json
import time
import os
        
from ETS2LA.Plugin import *
from ETS2LA.UI import *

available_channels = [
    {
        "channel": 0,
        "name": "Handshake",
        "description": "Reserved for initial handshake and connection setup.",
        "commands": [
            {
                "name": "available_channels",
                "method": "query",
                "description": "Returns a list of available channels and their descriptions."
            }
        ]
    },
    {
        "channel": 1,
        "name": "Transform",
        "description": "Current truck position and orientation in the game world.",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the truck position and orientation updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the truck position and orientation updates."
            }
        ]
    },
    {
        "channel": 2,
        "name": "Steering",
        "description": "The current steering plan of the truck. List of points along the path.",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the steering plan updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the steering plan updates."
            }
        ]
    },
    {
        "channel": 3,
        "name": "TruckStateData",
        "description": "API data for the current truck state. This includes speed, accel / braking, gear etc...",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the truck state data updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the truck state data updates."
            }
        ]
    }
]

class WebSocketConnection:
    def __init__(self, websocket):
        self.websocket = websocket
        self.queue = asyncio.Queue()
        self.sender_task = asyncio.create_task(self.send_messages())
        self.subscribed_channels = set()

    async def send_messages(self):
        try:
            while True:
                message = await self.queue.get()
                await self.websocket.send(message)
        except Exception as e:
            print("Client disconnected due to exception in send_messages.", str(e))

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Sockets V2",
        version="2.0",
        description="Unity visualization socket connection. Do not use!",
        modules=["TruckSimAPI"],
        tags=["WIP", "Visualization", "DO NOT USE"],
        hidden=True
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    fps_cap = 20
    
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

    async def handle_message(self, websocket, message):
        try:
            message = json.loads(message)
            method = message.get("method")
            channel = message.get("channel")
            params = message.get("params", {})

            if method == "query" and channel == 0:
                if params.get("name") == "available_channels":
                    response = {
                        "channel": 0,
                        "result": {
                            "type": "data",
                            "data": available_channels
                        }
                    }
                    await websocket.send(json.dumps(response))

            elif method == "subscribe":
                self.connected_clients[websocket].subscribed_channels.add(channel)
                response = {
                    "channel": channel,
                    "result": {
                        "type": "data",
                        "data": {
                            "message": f"Subscribed to channel {channel}."
                        }
                    }
                }
                logging.warning(f"Connection subscribed to channel {channel}.")
                await websocket.send(json.dumps(response))

            elif method == "unsubscribe":
                self.connected_clients[websocket].subscribed_channels.discard(channel)
                response = {
                    "channel": channel,
                    "result": {
                        "type": "data",
                        "data": {
                            "message": f"Unsubscribed from channel {channel}."
                        }
                    }
                }
                logging.warning(f"Connection unsubscribed from channel {channel}.")
                await websocket.send(json.dumps(response))

        except Exception as e:
            print("Error handling message:", str(e))

    async def server(self, websocket):
        print("Client Connected!")
        connection = WebSocketConnection(websocket)
        self.connected_clients[websocket] = connection
        print("Number of connected clients: ", len(self.connected_clients))
        try:
            async for message in websocket:
                print("Received message from client: ", message)
                await self.handle_message(websocket, message)
                
        except Exception as e:
            print("Client disconnected due to exception.", str(e))
        finally:
            connection.sender_task.cancel()
            del self.connected_clients[websocket]
            print("Client disconnected. Number of connected clients: ", len(self.connected_clients))

    def position(self, data):
        send = {
            "x": float(data["truckPlacement"]["coordinateX"]),
            "y": float(data["truckPlacement"]["coordinateY"]),
            "z": float(data["truckPlacement"]["coordinateZ"]),
        }
        
        rotationX = data["truckPlacement"]["rotationX"] * 360
        if rotationX < 0: rotationX += 360
        send["rx"] = float(rotationX)
        
        rotationY = data["truckPlacement"]["rotationY"] * 360
        send["ry"] = float(rotationY)
        
        rotationZ = data["truckPlacement"]["rotationZ"] * 360
        if rotationZ < 0: rotationZ += 360
        send["rz"] = float(rotationZ)
        
        return send
    
    def steering(self):
        points = self.plugins.Map
        
        send = {
            "points": [
                {
                    "x": point[0],
                    "y": point[1],
                    "z": point[2]
                } for point in points
            ]
        }
        
        return send
    
    def state_data(self, data):
        target_speed = self.globals.tags.acc
        target_speed = self.globals.tags.merge(target_speed)
        
        send = {
            "speed": data["truckFloat"]["speed"],
            "speed_limit": data["truckFloat"]["speedLimit"],
            "cruise_control": data["truckFloat"]["cruiseControlSpeed"],
            "target_speed": target_speed if target_speed else -1,
            "throttle": data["truckFloat"]["gameThrottle"],
            "brake": data["truckFloat"]["gameBrake"],
        }
        
        return send

    async def start(self):
        self.loop = asyncio.get_running_loop()
        async with websockets.serve(self.server, "localhost", 37522):
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
        
        print("Sockets waiting for client...")

    def run(self):
        api_data = TruckSimAPI.run()
        channel_data = {} # Cache data for each channel for a frame.
        
        try:
            for websocket, connection in list(self.connected_clients.items()):
                for channel in connection.subscribed_channels:
                    message = {}
                    if channel == 1:
                        if 1 not in channel_data:
                            channel_data[1] = self.position(api_data)
                            
                        message = {
                            "channel": 1,
                            "result": {
                                "type": "data",
                                "data": channel_data[1]
                            }
                        }
                    
                    if channel == 2:
                        if 2 not in channel_data:
                            channel_data[2] = self.steering()
                            
                        message = {
                            "channel": 2,
                            "result": {
                                "type": "data",
                                "data": channel_data[2]
                            }
                        }
                        
                    if channel == 3:
                        if 3 not in channel_data:
                            channel_data[3] = self.state_data(api_data)
                            
                        message = {
                            "channel": 3,
                            "result": {
                                "type": "data",
                                "data": channel_data[3]
                            }
                        }
                        
                    if message != {}:
                        asyncio.run_coroutine_threadsafe(connection.queue.put(json.dumps(message)), self.loop)
        except:
            logging.warning("Error sending data to clients.")
            pass