import asyncio
import websockets
import threading
from multiprocessing import Manager
import logging

connected = []

async def server(websocket, path):
    global connected
    # Register.
    connected.append(websocket)
    try:
        while True:
            # Wait for a message from the client
            await websocket.recv()
    except:
        connected.remove(websocket)
    finally:
        # Unregister.
        connected.remove(websocket)

import json
async def send_sonner(text, type):
    global connected
    message_dict = {"text": text, "type": type}
    message = json.dumps(message_dict)
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    await asyncio.wait(tasks)
    
def sonner(text, type="info"):
    """Send a sonner notification to the frontend.

    Args:
        text (str): Text to send.
        type (str, optional): Notification type. Defaults to "info". Available types are "info", "warning", "error" and "success".
    """
    asyncio.run(send_sonner(text, type))

async def start():
    wsServer = websockets.serve(server, "0.0.0.0", 37521)
    await wsServer

def run_thread():
    """Start the websocket server in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())
    loop.run_forever()

def run():
    logging.info("Starting the websocket server.")
    threading.Thread(target=run_thread, daemon=True).start()