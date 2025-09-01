"""
This file will expose ETS2LA via the zeroconf.
Clients can access ETS2LA via http://ets2la.local:port
"""

from zeroconf import Zeroconf, ServiceInfo
from ETS2LA.Utils.translator import _
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
    server=address,
)


def socket_thread():
    zeroconf = Zeroconf()
    zeroconf.register_service(info)

    logging.info(
        _(
            "Successfully registered [bold]http://{address}[/bold] to point to [dim]{local_ip}[/dim]."
        ).format(address=address[:-1], local_ip=local_ip)
    )

    try:
        while True:
            time.sleep(2)
            pass
    except Exception:
        pass

    zeroconf.unregister_service(info)
    zeroconf.close()


def run():
    threading.Thread(target=socket_thread, daemon=True).start()
