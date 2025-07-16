from ETS2LA.Utils.translator import _
from ETS2LA.Plugin import *
from ETS2LA.UI import *

from Plugins.NavigationSockets.projections import get_ets2_coordinates, get_ats_coordinates
from Plugins.NavigationSockets.socket import WebSocketConnection
from Plugins.Map.utils.math_helpers import DistanceBetweenPoints
import json
import math

last_angle = 0
last_position = (0, 0)

def degrees_to_radians(degrees):
    return degrees * math.pi / 180

def radians_to_degrees(radians):
    return radians * 180 / math.pi

def coords_to_wgs84(x, y, game="ETS2"):
    return get_ats_coordinates(x, y) if game == "ATS" else get_ets2_coordinates(x, y)

# https://github.com/Turfjs/turf/blob/master/packages/turf-bearing/index.ts
def bearing(start, end):
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

def convert_angle_to_wgs84_heading(position, speed, game="ETS2"):
    global last_position, last_angle

    if position == last_position:
        return last_angle

    last_wgs84 = coords_to_wgs84(*last_position, game=game)
    cur_wgs84 = coords_to_wgs84(*position, game=game)

    geographic_heading = bearing(last_wgs84, cur_wgs84)

    geographic_heading = (geographic_heading + 360) % 360
    
    if speed < 0:
        geographic_heading = (geographic_heading + 180) % 360
    
    last_position = position
    last_angle = geographic_heading

    return geographic_heading

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name=_("Navigation Sockets"),
        version="1.0",
        description=_("This plugin provides a WebSocket server for navigation data on a world map."),
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
        connection = WebSocketConnection(websocket)
        self.connected_clients[websocket] = connection
        response = [
            #{"id": 1,"result": {"type": "started"}},
            {"id": 2,"result": {"type": "started"}},
            #{"id": 3,"result": {"type": "started"}},
            {"id": 4,"result": {"type": "started"}},
            {"id": 5,"result": {"type": "started"}},
        ]
        try:
            async for message in websocket:
                # Respond to any message with the response
                await websocket.send(json.dumps(response))
                
                
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

    def run(self):
        data = TruckSimAPI.run()

        position = (data["truckPlacement"]["coordinateX"], data["truckPlacement"]["coordinateZ"])
        speed = data["truckFloat"]["speed"] * 1.25 # offset to make it zoom out faster
        game = data["scsValues"]["game"]
        
        if speed > 0.2 or speed < -0.2:
            rotation = convert_angle_to_wgs84_heading(position, speed, game=game)
        else:
            rotation = last_angle
            
        speed_mph = speed * 2.23694
        
        packets = [
        {
            "id": 2,
            "result": {
                "type": "data",
                "data": {
                    "position": coords_to_wgs84(*position, game=game),
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
                    "position": coords_to_wgs84(*position, game=game),
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
            
            nodes = navigation["nodes"]
            node_points = navigation["points"]
            
            total_points = []
            for i in range(len(nodes) - 1):
                node = nodes[i]
                points = node_points[i]
                
                if not points or len(points) < 5:
                    total_points.append([node.x, node.y, node.z])
                    continue
                
                start = points[0]
                end = points[-1]
                last = total_points[-1]
                
                distance_start = DistanceBetweenPoints(start, last)
                distance_end = DistanceBetweenPoints(end, last)
                
                if distance_end < distance_start:
                    # Reverse the points if the end point is closer to the last point
                    points = points[::-1]
                
                total_points.extend(points)
                
            packets.append({
                "id": "1",
                "result": {
                    "type": "data",
                    "data": {
                            "id": "1",
                            "segments": [
                                {
                                    "key": "route",
                                    "lonLats": [coords_to_wgs84(point[0], point[1], game=game) for point in total_points],
                                    "distance": math.sqrt((nodes[-1].x - nodes[0].x) ** 2 + (nodes[-1].y - nodes[0].y) ** 2),
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
