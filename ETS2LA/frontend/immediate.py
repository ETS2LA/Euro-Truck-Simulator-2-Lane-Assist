import websockets
import threading
import asyncio
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
        try:
            connected.remove(websocket)
        except:
            pass
    finally:
        # Unregister.
        try:
            connected.remove(websocket)
        except:
            pass

import json
async def send_sonner(text, type, sonnerPromise):
    global connected
    message_dict = {"text": text, "type": type, "promise": sonnerPromise}
    message = json.dumps(message_dict)
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    if tasks:  # Check if tasks list is not empty
        await asyncio.wait(tasks)
    
def sonner(text, type="info", sonnerPromise=""):
    """Send a sonner notification to the frontend.

    Args:
        text (str): Text to send.
        type (str, optional): Notification type. Defaults to "info". Available types are "info", "warning", "error", "success" and "promise".
    """
    asyncio.run(send_sonner(text, type, sonnerPromise))

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