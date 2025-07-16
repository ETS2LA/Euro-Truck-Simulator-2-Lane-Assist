import multiprocessing
import websockets
import threading
import logging
import asyncio
import socket
import json
import time
import math
import os
        
from ETS2LA.Utils.Values.numbers import SmoothedValue
from ETS2LA.Utils.translator import _
from ETS2LA.Plugin import *
from ETS2LA.UI import *

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
    },
    {
        "channel": 4,
        "name": "Traffic",
        "description": "Traffic data for the current game world.",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the traffic data updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the traffic data updates."
            }
        ]
    },
    {
        "channel": 5,
        "name": "Trailers",
        "description": "Data for the currently connected trailers.",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the trailer data updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the trailer data updates."
            }
        ]
    },
    {
        "channel": 6,
        "name": "Highlights",
        "description": "What UIDs to highlight in the game world. And any data associated with the highlights.",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the highlight data updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the highlight data updates."
            }
        ]
    },
    {
        "channel": 7,
        "name": "Status",
        "description": "Status of various app elements like steering and speed control.",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the status data updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the status data updates."
            }
        ]
    },
    {
        "channel": 8,
        "name": "Semaphores",
        "description": "Provides data for traffic lights and gates.",
        "commands": [
            {
                "name": "subscribe",
                "method": "subscribe",
                "description": "Subscribe to the semaphore data updates."
            },
            {
                "name": "unsubscribe",
                "method": "unsubscribe",
                "description": "Unsubscribe from the semaphore data updates."
            }
        ]
    }
]

class SettingsMenu(ETS2LAPage):
    refresh_rate = 0.5
    url = "/settings/VisualizationSockets"
    location = ETS2LAPageLocation.SETTINGS
    title = _("Visualization Sockets")

    def test(self):
        print("hi")
    
    def render(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            IP = s.getsockname()[0]
            s.close()
        except:
            IP = "127.0.0.1"

        TitleAndDescription(
            title=_("Visualization Sockets"),
            description=_("This plugin provides a websocket server for the ETS2LA Visualization.")
        )

        with Tabs():
            # TRANSLATORS: Host device in this context means the device that is running ETS2LA.
            with Tab(name=_("Host Device")):
                with Container(styles.FlexVertical() + styles.Gap("14px")):
                    Text(_("If you want to view the ETS2LA Visualization on the current device, simply open the 'Visualization' tab on the sidebar, you can then select between the official and Goodnightan mirrors."), style=styles.Description())
                    with Container(styles.FlexHorizontal() + styles.Gap("4px")):
                        Text(_("You can also use the following website:"), style=styles.Description())
                        Link("http://visualization.ets2la.com", "http://visualization.ets2la.com", styles.Classname("font-semibold text-sm"))

            with Tab(name=_("Other Device")):
                with Container(styles.FlexVertical() + styles.Gap("14px")):
                    if IP != "127.0.0.1":
                        with Container(styles.FlexVertical() + styles.Gap("6px")):
                            with Container(styles.FlexHorizontal() + styles.Gap("4px")):
                                Text(_("1. Open the following URL in your device's browser: "), style=styles.Description())
                                Link("http://visualization.ets2la.com", "http://visualization.ets2la.com", styles.Classname("font-semibold text-sm text-muted-foreground"))
                            Text(_("NOTE: You must load the site as http instead of https. Google Chrome will not work!"), styles.Classname("font-bold text-muted-foreground"))
                        with Container(styles.FlexVertical() + styles.Gap("6px")):
                            Text(_("2. Once the website loads press the red 'Remote Connection' button. If this doesn't connect then enter the following IP address:"), styles.Description())
                            Text(f"ws://{IP}:37522", styles.Classname("font-bold") + styles.Description())

                        Text(_("3. If you have any issues please verify that your device is on the same network as the host. You should also make sure that your firewall does not block the connection between the devices."), styles.Description())
                    else:
                        Text(_("Your IP address could not be found, this is likely due to a network issue. Viewing the visualization externally is not possible."), styles.Classname("font-bold") + styles.Description())

        Separator()
        
        if not self.plugin:
            Text(_("Waiting for plugin start..."), styles.Classname("font-bold"))
            return
        
        try:
            clients = self.plugin.connected_clients
        except:
            Text(_("Waiting for plugin to load..."), styles.Classname("font-bold"))
            return
        
        if len(clients) > 0:
            Text(_("The following clients are currently connected:"))
            with Container(styles.FlexVertical() + styles.Gap("14px")):
                for client in clients:
                    with Container(styles.FlexVertical() + styles.Gap("6px") + styles.Classname("border rounded-lg p-4 bg-input/10")):
                        with Container(styles.FlexHorizontal() + styles.Gap("4px")):
                            Text(f"{client.remote_address[0]}", styles.Classname("font-bold"))
                            Text(f"- {client.id}", styles.Classname("text-sm") + styles.Description())
                        connection = clients[client]
                        with Container(styles.FlexVertical() + styles.Gap("4px")):
                            Text("- " + _("Latency: {latency:.2f}ms").format(latency=client.latency * 1000), styles.Classname("text-sm"))
                            if connection.subscribed_channels:
                                Text("- " + _("Channels: {channels}").format(channels=", ".join(str(channel) for channel in connection.subscribed_channels)), styles.Classname("text-sm"))
                            else:
                                Text(_("Not acknowledged yet."), styles.Classname("font-semibold text-sm"))
        else:
            Text(_("There are no currently connected clients."), styles.Classname("font-bold"))

class WebSocketConnection:
    def __init__(self, websocket):
        self.websocket = websocket
        self.queue = asyncio.Queue()
        self.sender_task = asyncio.create_task(self.send_messages())
        self.subscribed_channels = set()
        self.acknowledged = False

    async def send_messages(self):
        try:
            while True:
                message = await self.queue.get()
                await self.websocket.send(message)
        except Exception as e:
            print("Client disconnected due to exception in send_messages.", str(e))

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name=_("Visualization Sockets"),
        version="2.0",
        description=_("This plugin provides a websocket server for the ETS2LA Visualization. It allows you to connect to the visualization from other devices and view the ETS2LA data in real-time."),
        modules=["TruckSimAPI", "Traffic", "Semaphores"],
        tags=["Base", "Visualization"],
        fps_cap=20
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    pages = [SettingsMenu]

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

    def Initialize(self):
        global TruckSimAPI
        global socket

        self.connected_clients = {}
        self.loop = None
        
        TruckSimAPI = self.modules.TruckSimAPI
        TruckSimAPI.TRAILER = True
        
        server_thread = threading.Thread(target=self.run_server_thread, daemon=True)
        server_thread.start()

    async def handle_message(self, websocket, message):
        try:
            message = json.loads(message)
            method = message.get("method")
            channel = message.get("channel", 0)
            params = message.get("params", {})
            
            if method == "acknowledge" and channel == 0:
                self.connected_clients[websocket].acknowledged = True

            elif method == "query" and channel == 0:
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
        print("Client connected")

        connection = WebSocketConnection(websocket)
        self.connected_clients[websocket] = connection
        print("Number of connected clients: ", len(self.connected_clients))
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except Exception as e:
            print("Client disconnected due to exception.", str(e))
        finally:
            connection.sender_task.cancel()
            del self.connected_clients[websocket]
            print("Client disconnected. Number of connected clients: ", len(self.connected_clients))
        
        

    def position(self, data):
        sector_coordinates = self.globals.tags.sector_center
        sector_coordinates = self.globals.tags.merge(sector_coordinates)
        if not sector_coordinates:
            sector_coordinates = (0, 0)
        
        send = {
            "x": float(data["truckPlacement"]["coordinateX"]),
            "y": float(data["truckPlacement"]["coordinateY"]),
            "z": float(data["truckPlacement"]["coordinateZ"]),
            "sector_x": sector_coordinates[0],
            "sector_y": sector_coordinates[1],
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
    
    def steering(self, data):
        points = self.globals.tags.steering_points
        points = self.globals.tags.merge(points)
        
        information = self.globals.tags.route_information
        information = self.globals.tags.merge(information)
        
        if not information:
            information = {}
            
        if not points:
            return {
                "points": [],
                "information": information
            }
        
        send = {
            "points": [
                {
                    "x": point[0],
                    "y": point[1],
                    "z": point[2]
                } for point in points
            ],
            "information": information # already a dictionary
        }
        
        return send
    
    def state_data(self, data):
        target_speed = self.globals.tags.acc
        target_speed = self.globals.tags.merge(target_speed)
        
        send = {
            "speed": data["truckFloat"]["speed"],
            "speed_limit": data["truckFloat"]["speedLimit"],
            "cruise_control": data["truckFloat"]["cruiseControlSpeed"],
            "target_speed": target_speed if target_speed else 0,
            "throttle": data["truckFloat"]["gameThrottle"],
            "brake": data["truckFloat"]["gameBrake"],
            "indicating_left": data["truckBool"]["blinkerLeftActive"],
            "indicating_right": data["truckBool"]["blinkerRightActive"],
            "indicator_left": data["truckBool"]["blinkerLeftOn"],
            "indicator_right": data["truckBool"]["blinkerRightOn"],
            "game": data["scsValues"]["game"],
            "time": data["commonUI"]["timeAbs"]
        }
        
        return send
    
    def traffic(self, data):
        vehicles = self.modules.Traffic.run()
        
        send = {
            "vehicles": [
                vehicle.__dict__() for vehicle in vehicles
            ]
        }
        
        return send
    
    smoothed_trailer_distances = [
        SmoothedValue("time", 0.5),
        SmoothedValue("time", 0.5),
        SmoothedValue("time", 0.5),
        SmoothedValue("time", 0.5),
    ]
    
    def trailers(self, data):
        trailer_data = []
        x = float(data["truckPlacement"]["coordinateX"])
        y = float(data["truckPlacement"]["coordinateY"])
        z = float(data["truckPlacement"]["coordinateZ"])
        
        id = 0
        for trailer in data["trailers"]:
            if trailer["comBool"]["attached"]:
                rotationX = trailer["comDouble"]["rotationX"] * 360
                if rotationX < 0: rotationX += 360
                rotationY = trailer["comDouble"]["rotationY"] * 360
                rotationZ = trailer["comDouble"]["rotationZ"] * 360
                
                hook_position = (trailer["conVector"]["hookPositionX"], trailer["conVector"]["hookPositionY"], trailer["conVector"]["hookPositionZ"])
                furthest_left_distance = 0
                furthest_left_position = 0
                furthest_right_distance = 0
                furthest_right_position = 0
                for i in range(len(trailer["conVector"]["wheelPositionX"])):
                    position = (trailer["conVector"]["wheelPositionX"][i], trailer["conVector"]["wheelPositionY"][i], trailer["conVector"]["wheelPositionZ"][i])
                    distance = math.sqrt((hook_position[0] - position[0])**2 + (hook_position[1] - position[1])**2 + (hook_position[2] - position[2])**2)
                    if position[0] < hook_position[0]:
                        if distance > furthest_left_distance:
                            furthest_left_distance = distance
                            furthest_left_position = i
                    else:
                        if distance > furthest_right_distance:
                            furthest_right_distance = distance
                            furthest_right_position = i
                
                trailer_position = (trailer["comDouble"]["worldX"], trailer["comDouble"]["worldY"], trailer["comDouble"]["worldZ"])
                distance = round(math.sqrt((trailer_position[0] - x)**2 + (trailer_position[1] - y)**2 + (trailer_position[2] - z)**2), 2)

                smoothed_trailer_distance = self.smoothed_trailer_distances[id]
                
                if abs(smoothed_trailer_distance.get() - distance) > 0.1:
                    difference = (smoothed_trailer_distance.get() - distance) 
                    vector_torwards_truck = (x - trailer_position[0], y - trailer_position[1], z - trailer_position[2])
                    vector_torwards_truck = (vector_torwards_truck[0] / distance, vector_torwards_truck[1] / distance, vector_torwards_truck[2] / distance)
                    trailer_position = (trailer_position[0] - vector_torwards_truck[0] * difference, trailer_position[1] - vector_torwards_truck[1] * difference, trailer_position[2] - vector_torwards_truck[2] * difference)
                    
                smoothed_trailer_distance.smooth(distance)
                
                trailer_data.append({
                    "x": trailer_position[0],
                    "y": trailer_position[1],
                    "z": trailer_position[2],
                    "rx": rotationX,
                    "ry": rotationY,
                    "rz": rotationZ,
                    "hook_x": hook_position[0],
                    "hook_y": hook_position[1],
                    "hook_z": hook_position[2],
                    "rear_left_x": trailer["conVector"]["wheelPositionX"][furthest_left_position],
                    "rear_left_y": trailer["conVector"]["wheelPositionY"][furthest_left_position],
                    "rear_left_z": trailer["conVector"]["wheelPositionZ"][furthest_left_position],
                    "rear_right_x": trailer["conVector"]["wheelPositionX"][furthest_right_position],
                    "rear_right_y": trailer["conVector"]["wheelPositionY"][furthest_right_position],
                    "rear_right_z": trailer["conVector"]["wheelPositionZ"][furthest_right_position],
                })
                
            id += 1
                
        return {
            "trailers": trailer_data
        }

    def highlights(self, data):
        vehicle_highlights = self.globals.tags.vehicle_highlights
        vehicle_highlights = self.globals.tags.merge(vehicle_highlights)
        
        aeb = self.globals.tags.AEB
        aeb = self.globals.tags.merge(aeb)
        
        send = {
            "aeb": aeb,
            "vehicles": vehicle_highlights, # list of UIDs
        }
        
        return send
    
    def status(self, data):
        status = self.globals.tags.status
        status = self.globals.tags.merge(status)
        
        if status is None:
            status = {}
        
        enabled = []
        disabled = []
        for key in status:
            if status[key]:
                enabled.append(key)
            else:
                disabled.append(key)
        
        send = {
            "enabled": enabled,
            "disabled": disabled
        }
        
        return send
    
    def semaphores(self, data):
        semaphores = self.modules.Semaphores.run()
        traffic_lights = [semaphore for semaphore in semaphores if semaphore.type == "traffic_light"]
        gates = [semaphore for semaphore in semaphores if semaphore.type == "gate"]
        
        send = {
            "traffic_lights": [
                semaphore.__dict__()
                for semaphore in traffic_lights
            ],
            "gates": [
                semaphore.__dict__()
                for semaphore in gates
            ]
        }
        return send

    async def start(self):
        self.loop = asyncio.get_running_loop()
        async with websockets.serve(self.server, "0.0.0.0", 37522):
            await asyncio.Future()  # run forever

    def run_server_thread(self):
        asyncio.run(self.start())

    def create_socket_message(self, channel, data):
        return {
            "channel": channel,
            "result": {
                "type": "data",
                "data": data
            }
        }

    channel_data_calls = {
        1: position,
        2: steering,
        3: state_data,
        4: traffic,
        5: trailers,
        6: highlights,
        7: status,
        8: semaphores
    }
    
    last_timestamp = 0

    def run(self):
        api_data = TruckSimAPI.run()
        channel_data = {} # Cache data for each channel for a frame.
        
        self.description.fps_cap = 20
        self.last_timestamp = api_data["time"]

        try:
            for websocket, connection in list(self.connected_clients.items()):
                if not connection.acknowledged:
                    continue
                
                for channel in connection.subscribed_channels:
                    try:
                        if channel not in channel_data:
                            if channel not in self.channel_data_calls:
                                logging.warning(f"Channel {channel} not implemented.")
                                continue    
                            channel_data[channel] = self.channel_data_calls[channel](self, api_data)
                            
                        message = self.create_socket_message(channel, channel_data[channel])
                        asyncio.run_coroutine_threadsafe(connection.queue.put(json.dumps(message)), self.loop)
                        
                    except Exception as e:
                        logging.warning(f"Error sending data to client: {str(e)} on channel {channel}.")
                
                connection.acknowledged = False
        except:
            pass # Got disconnected while iterating over the clients.
