from typing import Literal
import websockets
import threading
import asyncio
import logging
import json

connected = []

async def server(websocket, path):
    global connected
    connected.append(websocket)
    try:
        while True:
            await websocket.recv()
    except:
        try: connected.remove(websocket)
        except: pass
    finally:
        try: connected.remove(websocket)
        except: pass

async def send_sonner(text, type, sonnerPromise):
    global connected
    message_dict = {
        "text": text, 
        "type": type, 
        "promise": sonnerPromise
    }
    
    message = json.dumps(message_dict)
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    if tasks:
        await asyncio.wait(tasks)
    
    
def sonner(text:str, type:Literal["info", "warning", "error", "success", "promise"]="info", sonnerPromise:str=None):
    asyncio.run(send_sonner(text, type, sonnerPromise))

async def start():
    wsServer = websockets.serve(server, "0.0.0.0", 37521)
    await wsServer

def run_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())
    loop.run_forever()

def run():
    logging.info("Starting the websocket server.")
    threading.Thread(target=run_thread, daemon=True).start()