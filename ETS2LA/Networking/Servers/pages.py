from ETS2LA.Utils.functions import resolve_function_from_path
from ETS2LA.Handlers.pages import get_page, get_urls, get_page_names, page_function_call
import ETS2LA.Handlers.plugins as plugins
import ETS2LA.variables as variables 
from typing import Dict, Set
import websockets
import threading
import logging
import asyncio
import json
import time

subscribers: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
last_sent_data: Dict = {}  # stores the last JSON-serialized version of the page

def render_page(url: str):
    page_urls = get_urls()
    if url in page_urls:
        return get_page(url)
    else:
        return plugins.get_page_data(url)

def handle_functions(data: dict):
    page_urls = get_urls()
    page_names = get_page_names()
    
    url = data.get("url")
    func = data.get("target", "")
    args = data.get("args", [])
    
    if url in page_urls:
        try:
            name = page_names[page_urls.index(url)]
            if args:
                page_function_call(name, func.split(".")[-1], *args)
            else:
                page_function_call(name, func.split(".")[-1])
        except Exception as e:
            logging.exception(f"Error calling function {func} with args {args}: {e}")
        
    else:
        pages = plugins.get_page_list()
        plugin = ''
        for _, page in pages.items():
            if page["url"] == url:
                plugin = page["plugin"]
                break
        
        if plugin:
            plugins.function_call(
                name=plugin,
                function=func,
                args=args,
            )

# Send updated page data to all subscribers of a given URL
async def push_update(url: str):
    current_data = render_page(url)
    dead_sockets = set()
    
    if last_sent_data[url] != current_data:
        last_sent_data[url] = current_data
        for ws in subscribers.get(url, []):
            try:
                await ws.send(json.dumps({
                    "url": url,
                    "data": current_data
                }))
            except websockets.ConnectionClosed:
                dead_sockets.add(ws)

    # Clean up disconnected clients
    for ws in dead_sockets:
        subscribers[url].discard(ws)

# Handles incoming websocket connections
async def handler(ws, path):
    ip = ws.remote_address[0]
    logging.info(f"UI client connected from [dim]{ip}[/dim]")
    try:
        async for message in ws:
            try:
                data = json.loads(message)
                if data.get("type") == "subscribe":
                    url = data.get("url")
                    if url not in subscribers:
                        subscribers[url] = set()

                    if ws not in subscribers[url]:
                        subscribers[url].add(ws)

                    # Send page data immediately
                    current_data = render_page(url)
                    last_sent_data[url] = json.dumps(current_data)
                    await ws.send(json.dumps({
                        "url": url,
                        "data": current_data
                    }))
                
                if data.get("type") == "unsubscribe":
                    url = data.get("url")
                    if url in subscribers:
                        subscribers[url].discard(ws)
                        if not subscribers[url]:
                            del subscribers[url]
                            
                if data.get("type") == "function":
                    handle_functions(data["data"])
                            
            except Exception as e:
                logging.exception(f"Error handling message from {ip}: {e}")
    finally:
        logging.info(f"UI client disconnected from [dim]{ip}[/dim]")
        for s in subscribers.values():
            s.discard(ws)

# Background task to check for updates periodically
async def update_loop():
    last_update = time.perf_counter()
    while True:
        await asyncio.gather(*(push_update(url) for url in subscribers))
        variables.REFRESH_PAGES = False
        while not variables.REFRESH_PAGES:
            await asyncio.sleep(0.05) # Cap to 20fps at max refreshrate.
            if time.perf_counter() - last_update > 2:
                break

# Start server + updater loop
async def start():
    server = await websockets.serve(handler, "0.0.0.0", 37523)
    logging.info("WebSocket server started on ws://0.0.0.0:37523")
    await update_loop()

# Threaded entry point
def run_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())
    loop.run_forever()

def run():
    threading.Thread(target=run_thread, daemon=True).start()
    logging.info("UI Sockets server running at ws://0.0.0.0:37523")
