"""
This file provides a websocket server that can send notifications
to the frontend. Below is the format that the frontend can
expect to receive data in:

sonner (notification):
{
    "text": "This is a notification",
    "type": "info | warning | error | success",
    "promise": "promiseId" # NOTE: Promise is deprecated!
}

ask (question):
{
    "ask": {
        "text": "What is your name?",
        "options": ["John", "Doe"],
        "description": "Please select your name."
    }
}

ask (response from frontend):
{
    "response": "John"
}

navigate (navigate):
{
    "page": "url/to/the/page"
}

dialog (open dialog):
{
    "dialog": {
        "json": {}
    }
}
"""

from ETS2LA.Utils.translator import Translate
from ETS2LA.Handlers import sounds

from typing import Literal
import logging
import json

import websockets
import threading
import asyncio

connected = {}
"""
Connected websockets and their messages.
```
{
    websocket: message
}
```
"""

condition = threading.Condition()
"""Threading condition to wait for a response"""

async def server(websocket, path) -> None:
    """
    The main websocket server that listens for client's
    messages. Please note that this server is called
    for every new connection!
    
    :param websocket: The websocket object (filled by websockets)
    :param path: The path that the client (filled by websockets)
    """
    
    global connected
    connected[websocket] = None
    try:
        while True:
            # Blocking until a message is received
            # or the connection is closed.
            try: message = await websocket.recv()
            except: break
            
            # Handle the message
            if message != None:
                try:
                    message = json.loads(message)
                except: pass

                with condition:
                    connected[websocket] = message
                    condition.notify_all()
    except:
        logging.exception(Translate("immediate.message_error"))
        pass
    
    finally:
        # Remove the websocket from the connected list
        connected.pop(websocket, None)

async def send_sonner(text: str, 
                      type: Literal["info", "warning", "error", "success", "promise"]="info", 
                      sonner_promise: str | None = None) -> None:
    """
    Will send a notification to all connected clients.
    This function is blocking until all messages are sent.
    
    :param str text: The text of the notification
    :param str type: The type of the notification
    :param str sonner_promise: The promise ID (deprecated)
    """
    
    global connected
    message_dict = {
        "text": text, 
        "type": type, 
        "promise": sonner_promise
    }
    
    message = json.dumps(message_dict)
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    if tasks:
        await asyncio.wait(tasks)
        
def sonner(text: str, 
           type: Literal["info", "warning", "error", "success", "promise"]="info", 
           sonner_promise: str | None = None) -> None:
    """
    Blocking non-async function that will send a notification to all connected clients.
    """
    asyncio.run(send_sonner(text, type, sonner_promise))

async def send_ask(text: str, options: list[str], description: str) -> dict:
    """
    Will send a dialog with a question with the given options.
    This function is blocking until a response is received.
    
    :param str text: The text of the question
    :param list[str] options: The options to choose from
    :param str description: The description of the question
    
    :return str: The response from the client
    """
    global connected
    message_dict = {
        "ask": {
            "text": text, 
            "options": options,
            "description": description
        }
    }
    
    message = json.dumps(message_dict)
    
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    if tasks:
        await asyncio.wait(tasks)
    
    # Wait for a response from all connected clients
    # TODO: This might deadlock?
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
    
def ask(text: str, options: list, description: str = "") -> dict:
    """
    Non-async function that will send a dialog with a question with the given options.
    """
    sounds.Play('info')
    response = asyncio.run(send_ask(text, options, description))
    return response

async def send_navigate(url: str, sender: str, reason: str = "") -> None:
    """
    Send a command to the frontend to navigate to a new page.
    
    :param str url: The page to navigate to.
    """
    global connected
    message_dict = {
        "navigate": {
            "url": url,
            "reason": reason,
            "sender": sender
        }
    }
    
    message = json.dumps(message_dict)
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    if tasks:
        await asyncio.wait(tasks)

def navigate(url: str, sender: str, reason: str = "") -> None:
    """
    Non-async function that will send a command to the frontend to navigate to a new page.
    """
    if url == "":
        logging.error(Translate("immediate.empty_page"))
        return
    asyncio.run(send_navigate(url, sender, reason))

async def send_dialog(json_data: dict, no_response: bool = False) -> dict | None:
    """
    Send a dialog with the given json data to all connected clients.
    Will wait for a response if no_response is False.
    
    :param dict json_data: The JSON data to send to the dialog
    :param bool no_response: If True, this function will not wait for a response.
    
    :return dict: The response from the client
    """
    global connected
    message_dict = {
        "dialog": {
            "json": json_data
        }
    }
    
    message = json.dumps(message_dict)
    tasks = [asyncio.create_task(ws.send(message)) for ws in connected]
    if tasks:
        await asyncio.wait(tasks)
        
    # Wait for a response from all connected clients
    response = None
    if not no_response:
        while response is None:
            with condition:
                condition.wait()
                for ws in connected:
                    response = connected[ws]
                    if response != None:
                        connected[ws] = None
                        break
        
    return response

def dialog(ui: dict, no_response: bool = False) -> dict | None:
    """
    Non-async function that will send a dialog with the given json data to all connected clients.
    
    :param dict ui: The JSON data to send to the dialog
    :param bool no_response: If True, this function will not wait for a response.
    
    :return dict | None: The response from the client
    """
    sounds.Play('info')
    response = asyncio.run(send_dialog(ui, no_response))
    return response

async def start() -> None:
    """
    Serve the websocket server on 0.0.0.0 and port 37521.
    """
    wsServer = websockets.serve(server, "0.0.0.0", 37521, logger=logging.Logger("null"))
    await wsServer

def run_thread():
    """
    Run the websocket server in a new thread.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())
    loop.run_forever()

def run():
    """
    Non-async function that will start the websocket server
    on a dedicated thread. This thread is a daemon so it will
    close when the parent thread closes.
    """
    threading.Thread(target=run_thread, daemon=True).start()
    logging.info(Translate("immediate.websocket_started"))