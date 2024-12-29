from ETS2LA.Plugin import *
from ETS2LA.UI import *

import math

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = False
    plugin_name = "Sockets"
    def render(self):
        Label("Sockets Settings", classname_preset=TitleClassname)
        Label("This is the plugin that sends data to the visualization sockets.", classname_preset=DescriptionClassname)
        Slider("Data FPS", "update_rate", 30, 10, 60, 1, description="How many times per second the data being sent to the clients is updated.", requires_restart=True)
        return RenderUI()

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
                await asyncio.sleep(1/60)  # Limit to 60 fps
        except Exception as e:
            print("Client disconnected due to exception in send_messages.", str(e))

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="plugins.sockets",
        version="1.0",
        description="plugins.sockets.description",
        modules=["TruckSimAPI"],
        tags=["Base", "Visualization", "Frontend"]
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    settings_menu = SettingsMenu()
    
    def init(self):
        self.connected_clients = {}
        self.loop = None

    def imports(self):
        global multiprocessing, websockets, threading, logging, asyncio, json, os, zlib, time
        import multiprocessing
        import websockets
        import threading
        import logging
        import asyncio
        import json
        import zlib
        import time
        import os

    async def server(self, websocket):
        print("Client Connected!")
        connection = WebSocketConnection(websocket)
        self.connected_clients[websocket] = connection
        print("Number of connected clients: ", len(self.connected_clients))
        try:
            async for message in websocket:
                pass  # Handle incoming messages if necessary
        except Exception as e:
            print("Client disconnected due to exception.", str(e))
        finally:
            connection.sender_task.cancel()
            del self.connected_clients[websocket]
            print("Client disconnected. Number of connected clients: ", len(self.connected_clients))

    def position(self, data):
        send = ""
        send += "x:" + str(data["truckPlacement"]["coordinateX"]) + ";"
        send += "y:" + str(data["truckPlacement"]["coordinateY"]) + ";"
        send += "z:" + str(data["truckPlacement"]["coordinateZ"]) + ";"
        rotationX = data["truckPlacement"]["rotationX"] * 360
        if rotationX < 0: rotationX += 360
        send += "rx:" + str(rotationX) + ";"
        rotationY = data["truckPlacement"]["rotationY"] * 360
        send += "ry:" + str(rotationY) + ";"
        rotationZ = data["truckPlacement"]["rotationZ"] * 360
        if rotationZ < 0: rotationZ += 360
        send += "rz:" + str(rotationZ) + ";"
        return send

    def trailer(self, data):
        send = "JSONtrailers:[];"
        trailer_data = []
        for trailer in data["trailers"]:
            if trailer["comBool"]["attached"]:
                rotationX = trailer["comDouble"]["rotationX"] * 360
                if rotationX < 0: rotationX += 360
                rotationY = trailer["comDouble"]["rotationY"] * 360
                if rotationY < 0: rotationY += 360
                rotationZ = trailer["comDouble"]["rotationZ"] * 360
                if rotationZ < 0: rotationZ += 360
                
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
                
                trailer_data.append({
                    "x": trailer["comDouble"]["worldX"],
                    "y": trailer["comDouble"]["worldY"],
                    "z": trailer["comDouble"]["worldZ"],
                    "rx": rotationX,
                    "ry": rotationY,
                    "rz": rotationZ,
                    "hookX": hook_position[0],
                    "hookY": hook_position[1],
                    "hookZ": hook_position[2],
                    "leftX": trailer["conVector"]["wheelPositionX"][furthest_left_position],
                    "leftY": trailer["conVector"]["wheelPositionY"][furthest_left_position],
                    "leftZ": trailer["conVector"]["wheelPositionZ"][furthest_left_position],
                    "rightX": trailer["conVector"]["wheelPositionX"][furthest_right_position],
                    "rightY": trailer["conVector"]["wheelPositionY"][furthest_right_position],
                    "rightZ": trailer["conVector"]["wheelPositionZ"][furthest_right_position],
                })
            
        if trailer_data != []: send = "JSONtrailers:" + json.dumps(trailer_data) + ";"
            
        return send

    def traffic_lights(self, data):
        data["TrafficLights"] = self.globals.tags.TrafficLights
        data["TrafficLights"] = self.globals.tags.merge(data["TrafficLights"])
        try:
            send = "JSONTrafficLights:" + json.dumps(data["TrafficLights"]) + ";"
        except:
            for i in range(0, len(data["TrafficLights"])):
                data["TrafficLights"][i] = data["TrafficLights"][i].json()
            send = "JSONTrafficLights:" + json.dumps(data["TrafficLights"]) + ";"
        return send

    def speed(self, data):
        data["targetSpeed"] = self.globals.tags.acc
        data["targetSpeed"] = self.globals.tags.merge(data["targetSpeed"])
        
        if data["targetSpeed"] is None:
            data["targetSpeed"] = data["truckFloat"]["cruiseControlSpeed"]
                
        send = "speed:" + str(data["truckFloat"]["speed"]) + ";"
        send += "speedLimit:" + str(data["truckFloat"]["speedLimit"]) + ";"
        send += "cc:" + str(data["targetSpeed"]) + ";"
        return send

    def accelBrake(self, data):
        send = "accel:" + str(data["truckFloat"]["gameThrottle"]) + ";"
        send += "brake:" + str(data["truckFloat"]["gameBrake"]) + ";"
        return send

    lastVehicles = [""]
    lastVehicleString = ""
    def vehicles(self, data):
        data["vehicles"] = self.globals.tags.vehicles
        data["vehicles"] = self.globals.tags.merge(data["vehicles"])
        
        if data["vehicles"] is None or type(data["vehicles"]) != list or data["vehicles"] == [] or type(data["vehicles"][0]) != dict:
            return "JSONvehicles:[];"
        
        try:    
            if data["vehicles"] == self.lastVehicles:
                return self.lastVehicleString
        except:
            return self.lastVehicleString
        
        if data["vehicles"] is not None:
            newVehicles = []
            try:
                for vehicle in data["vehicles"]:
                    if isinstance(vehicle, dict):
                        newVehicles.append(vehicle)
                    elif isinstance(vehicle, list): # No clue why this happens, it's just sometimes single coordinates like this [31352.055901850657, 18157.970393701282]
                        continue
                    elif isinstance(vehicle, tuple):
                        continue
                    elif isinstance(vehicle, str):
                        continue
                    else:
                        try:
                            newVehicles.append(vehicle.json())
                        except:
                            try:
                                newVehicles.append(vehicle.__dict__)
                            except:
                                pass
            except:
                pass
                        
            data["vehicles"] = newVehicles
        
        if data["vehicles"] is []:
            return "JSONvehicles:[];"
            
        send = "JSONvehicles:" + json.dumps(data["vehicles"]) + ";"
        self.lastVehicles = data["vehicles"]
        self.lastVehicleString = send
        return send

    lastObjects = [""]
    lastObjectString = ""
    def objects(self, data):
        data["objects"] = self.globals.tags.objects
        data["objects"] = self.globals.tags.merge(data["objects"])
        
        if data["objects"] is None or type(data["objects"]) != list or data["objects"] == [] or type(data["objects"][0]) != dict:
            return "JSONobjects:[];"
        
        try:    
            if data["objects"] == self.lastObjects:
                return self.lastObjectString
        except:
            return self.lastObjectString
        
        if data["objects"] is not None:
            newObjects = []
            try:
                for obj in data["objects"]:
                    if isinstance(obj, dict):
                        newObjects.append(obj)
                    elif isinstance(obj, list): # No clue why this happens, it's just sometimes single coordinates like this [31352.055901850657, 18157.970393701282]
                        continue
                    elif isinstance(obj, tuple):
                        continue
                    elif isinstance(obj, str):
                        continue
                    else:
                        try:
                            newObjects.append(obj.json())
                        except:
                            try:
                                newObjects.append(obj.__dict__)
                            except:
                                pass
            except:
                pass
                        
            data["objects"] = newObjects
        
        if data["objects"] is []:
            return "JSONobjects:[];"
            
        send = "JSONobjects:" + json.dumps(data["objects"]) + ";"
        self.lastObjects = data["objects"]
        self.lastObjectString = send
        return send

    lastSteeringPoints = []
    def steering(self, data):
        try:
            steeringPoints = []
            data["steeringPoints"] = self.plugins.Map
            if data["steeringPoints"] is not None:
                for point in data["steeringPoints"]:
                    steeringPoints.append(point)
                self.lastSteeringPoints = steeringPoints
            else:
                steeringPoints = self.lastSteeringPoints
            
            send = "JSONsteeringPoints:" + json.dumps(steeringPoints) + ";"
            return send
        except:
            return "JSONsteeringPoints:[];"
        
    def status(self, data):
        try:
            data["status"] = self.globals.tags.status
            data["status"] = self.globals.tags.merge(data["status"])
            if data["status"] is None or type(data["status"]) != dict:
                return 'JSONstatus:{};'
            send = "JSONstatus:" + json.dumps(data["status"]) + ";"
            return send
        except:
            logging.exception("Error in status")
            return 'JSONstatus:{};'
        
    def acc_status(self, data):
        try:
            data["acc_status"] = self.globals.tags.acc_status
            data["acc_status"] = self.globals.tags.merge(data["acc_status"])
            if data["acc_status"] is None or type(data["acc_status"]) != str:
                return 'acc_status:ACC status error;'
            send = "acc_status:" + data["acc_status"] + ";"
            return send
        except:
            logging.exception("Error in acc_status")
            return 'acc_status:ACC status error;'
        
    lastHiglights = ""
    def highlights(self, data):
        try:
            data["highlights"] = self.globals.tags.highlights
            data["highlights"] = self.globals.tags.merge(data["highlights"])
            if data["highlights"] is None or type(data["highlights"]) != list:
                data["highlights"] = self.lastHiglights
            else:
                self.lastHiglights = data["highlights"]
                
            send = "highlights:" + json.dumps(data["highlights"]) + ";"
            return send
        except:
            logging.exception("Error in highlights")
            return 'highlights:[];'
            
    lastInstruct = [{}]
    def instruct(self, data):
        try:
            data["instruct"] = self.globals.tags.instruct
            data["instruct"] = self.globals.tags.merge(data["instruct"])
            if data["instruct"] is None or type(data["instruct"]) != list:
                data["instruct"] = self.lastInstruct
            else:
                self.lastInstruct = data["instruct"]

            send = "instruct:" + json.dumps(data["instruct"][:4] + [data["instruct"][-1]]) + ";"
            return send
        except:
            return ""

    def stopping_distance(self, data):
        try:
            data["stopping_distance"] = self.globals.tags.stopping_distance
            data["stopping_distance"] = self.globals.tags.merge(data["stopping_distance"])

            if data["stopping_distance"] is None or type(data["stopping_distance"]) not in [int, float]:
                data["stopping_distance"] = -1

            send = "stopping_distance:" + str(data["stopping_distance"]) + ";"
            return send
        except:
            return ""

    def lateral_offset(self, data):
        try:
            data["lateral_offset"] = self.globals.tags.lateral_offset
            data["lateral_offset"] = self.globals.tags.merge(data["lateral_offset"])
            
            if data["lateral_offset"] is None:
                data["lateral_offset"] = 0

            send = "lateral_offset:" + str(data["lateral_offset"]) + ";"
            return send
        except:
            return ""

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
        
        print("Visualization sockets waiting for client...")
        
    def compress_data(self, data):
       #Check if on linux
        compressor = zlib.compressobj(wbits=28)
        compressed_data = compressor.compress(data)
        compressed_data += compressor.flush()
        return compressed_data

    # Example usage in your server function
    def run(self):
        self.fps_cap = self.settings.update_rate
        if self.fps_cap is None:
            self.fps_cap = 20
            self.settings.update_rate = 20
        
        data = TruckSimAPI.run()

        tempSend = ""
        tempSend += self.position(data)
        tempSend += self.trailer(data)
        tempSend += self.speed(data)
        tempSend += self.accelBrake(data)
        tempSend += self.vehicles(data)
        tempSend += self.objects(data)
        tempSend += self.traffic_lights(data)
        tempSend += self.steering(data)
        tempSend += self.acc_status(data)
        tempSend += self.status(data)
        tempSend += self.highlights(data)
        tempSend += self.instruct(data)
        tempSend += self.stopping_distance(data)
        tempSend += self.lateral_offset(data)

        #Switch to zlib when on windows
        if os.name == "nt":
            compressed_message = zlib.compress(tempSend.encode("utf-8"), wbits=28)
        else:
            compressed_message = self.compress_data(tempSend.encode("utf-8"))
            
        # Enqueue the message to all connected clients
        for connection in list(self.connected_clients.values()):
            asyncio.run_coroutine_threadsafe(connection.queue.put(compressed_message), self.loop)