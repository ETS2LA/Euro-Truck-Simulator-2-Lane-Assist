from ETS2LA.Plugin import *
from ETS2LA.UI import *

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = False
    plugin_name = "Sockets"
    def render(self):
        Title("Sockets Settings")
        Description("This is the plugin that sends data to the visualization sockets.")
        Slider("Data FPS", "update_rate", 30, 10, 60, 1, description="How many times per second the data being sent to the clients is updated.", requires_restart=True)
        return RenderUI()

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="plugins.sockets",
        version="1.0",
        description="plugins.sockets.description",
        modules=["TruckSimAPI"],
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )
    
    settings_menu = SettingsMenu()
    
    send = ""
    connected_clients = []
    
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
        self.connected_clients.append(websocket)  # Step 2: Add a client to the list when they connect
        print("Number of connected clients: ", len(self.connected_clients))
        try:
            while True:
                if self.send:
                    await websocket.send(self.send)
                    # Wait for acknowledgment from client
                    try:
                        ack = await websocket.recv()
                    except Exception as e:
                        print("Client disconnected while receiving data.", str(e))
                        break
                    if ack != "ok":
                        print(f"Unexpected message from client: {ack}")
        except Exception as e:
            print("Client disconnected due to exception.", str(e))
        finally:
            self.connected_clients.remove(websocket)  # Step 3: Remove a client from the list when they disconnect

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
        
    lastStatus = ""
    def status(self, data):
        try:
            data["status"] = self.globals.tags.status
            data["status"] = self.globals.tags.merge(data["status"])
            if data["status"] is None or type(data["status"]) != str:
                data["status"] = self.lastStatus
            else:
                self.lastStatus = data["status"]
            send = "status:" + data["status"] + ";"
            return send
        except:
            logging.exception("Error in status")
            return 'status:ACC status error;'
        
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

    async def start_server(self, func):
        async with websockets.serve(func, "localhost", 37522):
            await asyncio.Future() # run forever
            
    def run_server_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_server(self.server))
        loop.run_forever()

    def Initialize(self):
        global TruckSimAPI
        global socket
        
        TruckSimAPI = self.modules.TruckSimAPI
        TruckSimAPI.TRAILER = True
        
        socket = threading.Thread(target=self.run_server_thread)
        socket.start()
        
        print("Visualization sockets waiting for client...")
        
    def compress_data(self, data):
        compressor = zlib.compressobj(wbits=28)
        compressed_data = compressor.compress(data)
        compressed_data += compressor.flush()
        return compressed_data

    # Example usage in your server function
    def run(self):
        self.fps_cap = self.settings.update_rate
        if self.fps_cap is None:
            self.fps_cap = 30
            self.settings.update_rate = 30
        
        data = TruckSimAPI.run()

        tempSend = ""
        tempSend += self.position(data)
        tempSend += self.speed(data)
        tempSend += self.accelBrake(data)
        tempSend += self.vehicles(data)
        tempSend += self.objects(data)
        tempSend += self.traffic_lights(data)
        tempSend += self.steering(data)
        tempSend += self.status(data)
        tempSend += self.highlights(data)
        tempSend += self.instruct(data)
        tempSend += self.stopping_distance(data)

        #Switch to zlib when on windows
        if os.name == "nt":
            self.send = zlib.compress(tempSend.encode("utf-8"), wbits=28)
        else:
            self.send = compress_data(tempSend.encode("utf-8"))