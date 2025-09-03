from ETS2LA.Handlers.pages import (
    get_page,
    get_urls,
    get_page_names,
    page_function_call,
    open_event,
    close_event,
)
import ETS2LA.Handlers.plugins as plugins
import ETS2LA.variables as variables
from typing import Dict
import websockets
import threading
import logging
import asyncio
import json
import time

connected: Dict[websockets.WebSocketServerProtocol, list[str]] = {}
"""
{
    websocket: [url1, url2, ...]
}
"""


# Send an open event to the page object
# that matches the URL.
def send_open_event(url: str):
    page_urls = get_urls()
    if url in page_urls:
        page_names = get_page_names()
        name = page_names[page_urls.index(url)]
        open_event(name)
    else:
        plugins.page_open_event(url)


# Send a close event to the page object
# that matches the URL.
def send_close_event(url: str):
    page_urls = get_urls()
    if url in page_urls:
        page_names = get_page_names()
        name = page_names[page_urls.index(url)]
        close_event(name)
    else:
        plugins.page_close_event(url)


# Render the given page URL.
def render_page(url: str):
    page_urls = get_urls()
    if url in page_urls:
        return get_page(url)
    else:
        return plugins.get_page_data(url)


# Handle a function call from the frontend.
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
        plugin = ""
        for _, page in pages.items():
            if page["url"] == url:
                plugin = page["plugin"]
                break

        if plugin:
            plugins.function_call(
                id=plugin,
                function=func,
                args=args,
            )


# Send updated page data to all subscribers of a given URL
async def push_update(url: str):
    websockets = []
    for ws, urls in connected.items():
        if url in urls:
            websockets.append(ws)

    current_data = render_page(url)
    current_data = json.dumps(current_data)

    for ws in websockets:
        await ws.send('{"url": "' + url + '", "data": ' + current_data + "}")


# Websocket handler itself, ws.recv() will block until a message is received
async def handler(ws: websockets.WebSocketServerProtocol, path):
    global connected
    connected[ws] = []
    try:
        while True:
            try:
                message = await ws.recv()
            except Exception:
                break

            if message:
                data = json.loads(message)
                if data.get("type") == "subscribe":
                    url = data.get("url")
                    if url not in connected[ws]:
                        connected[ws].append(url)

                    send_open_event(url)

                    current_data = render_page(url)
                    current_data = json.dumps(current_data)
                    await ws.send(json.dumps({"url": url, "data": current_data}))

                elif data.get("type") == "unsubscribe":
                    url = data.get("url")
                    if url in connected[ws]:
                        connected[ws].remove(url)
                        send_close_event(url)

                elif data.get("type") == "function":
                    handle_functions(data["data"])

    except Exception:
        logging.exception("An error occurred while processing a message.")
    finally:
        connected.pop(ws, None)


# Background task to check for updates periodically
async def update_loop():
    last_update = 0
    while True:
        last_update = time.perf_counter()

        urls = []
        for websocket in connected:
            for url in connected[websocket]:
                if url not in urls:
                    urls.append(url)
        await asyncio.gather(*(push_update(url) for url in urls))

        variables.REFRESH_PAGES = False
        while not variables.REFRESH_PAGES:
            await asyncio.sleep(0.05)
            if time.perf_counter() - last_update > 2:
                break


# Start server + updater loop
async def start():
    server = websockets.serve(handler, "0.0.0.0", 37523)
    await server
    await update_loop()


# Threaded entry point
def run_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start())


def run():
    threading.Thread(target=run_thread, daemon=True).start()
