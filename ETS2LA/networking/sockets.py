import multiprocessing
import websockets
import logging
import asyncio
import json

async def server(websocket):
    print("Client Connected!")
    import ETS2LA.modules.TruckSimAPI.main as TruckSimAPI
    TruckSimAPI.Initialize()
    TruckSimAPI.TRAILER = True
    
    while True:
        data = TruckSimAPI.run()
        # Get the data we need to send
        send = ""
        send += "x:" + str(data["truckPlacement"]["coordinateX"]) + ","
        send += "y:" + str(data["truckPlacement"]["coordinateY"]) + ","
        send += "z:" + str(data["truckPlacement"]["coordinateZ"]) + ","
        rotationX = data["truckPlacement"]["rotationX"] * 360
        if rotationX < 0: rotationX += 360
        send += "rx:" + str(rotationX) + ","
        rotationY = data["truckPlacement"]["rotationY"] * 360
        if rotationY < 0: rotationY += 360
        send += "ry:" + str(rotationY) + ","
        rotationZ = data["truckPlacement"]["rotationZ"] * 360
        if rotationZ < 0: rotationZ += 360
        send += "rz:" + str(rotationZ) + ","
        try:
            await websocket.send(send)

            # Wait for acknowledgment from client
            ack = await websocket.recv()
        except:
            print("Client disconnected.")
            break
        if ack != "ok":
            print(f"Unexpected message from client: {ack}")

def run_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print("Visualization sockets waiting for client...")
    start_server = websockets.serve(server, "localhost", 37522)
    loop.run_until_complete(start_server)
    loop.run_forever()

def run():
    process = multiprocessing.Process(target=run_server, daemon=True)
    process.start()