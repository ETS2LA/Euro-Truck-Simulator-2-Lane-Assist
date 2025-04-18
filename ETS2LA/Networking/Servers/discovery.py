"""
This file will expose ETS2LA via the zeroconf.
Clients can access ETS2LA via http://ets2la.local:port
"""

from zeroconf import Zeroconf, ServiceInfo
import threading
import logging
import socket
import time


service_name = "ETS2LA._http._tcp.local."
address = "ets2la.local."
port = 37520

local_ip = socket.gethostbyname(socket.gethostname())

info = ServiceInfo(
    "_http._tcp.local.",
    service_name,
    addresses=[socket.inet_aton(local_ip)],
    port=port,
    properties={},
    server=address
)

def socket_thread():
    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    
    logging.info(f"Successfully registered [bold]http://{address[:-1]}[/bold] to point to [dim]{local_ip}[/dim].")
    
    try:
        while True:
            time.sleep(2)
            pass
    except:
        pass
    
    zeroconf.unregister_service(info)
    zeroconf.close()
    

def run():
    threading.Thread(target=socket_thread, daemon=True).start()