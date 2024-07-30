from typing import Literal
import websockets
import threading
import asyncio
import logging
import json

connected = {}
responses = {}

condition = threading.Condition()

async def server(websocket, path):
    global connected
    connected[websocket] = None
    try:
        while True:
            message = await websocket.recv()
            if message != None:
                try:
                    message = json.loads(message)
                except:
                    pass
                # print(f"Received message: {message}")
                with condition:
                    connected[websocket] = message
                    condition.notify_all()
    except:
        logging.exception("An error occurred while processing a message.")
        pass
    finally:
        connected.pop(websocket, None)

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

async def send_ask(text, options):
    global connected
    message_dict = {
        "ask": {
            "text": text, 
            "options": options
        }
    }
    
    message = json.dumps(message_dict)
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    if tasks:
        await asyncio.wait(tasks)
    
    response = None
    while response is None:
        with condition:
            condition.wait()
            for ws in connected:
                response = connected[ws]
                if response != None:
                    connected[ws] = None
                    break
        
    return response
    
def ask(text:str, options:list):
    response = asyncio.run(send_ask(text, options))
    return response

async def send_page(page):
    global connected
    message_dict = {
        "page": page
    }
    
    message = json.dumps(message_dict)
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    if tasks:
        await asyncio.wait(tasks)
        
def page(page:str):
    if page == "":
        logging.error("Tried to send an empty page.")
        return
    asyncio.run(send_page(page))

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