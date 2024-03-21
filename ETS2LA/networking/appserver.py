import rpyc
from rpyc.utils.server import ThreadedServer
import threading
import logging
import os

class ETS2LAInternalService(rpyc.Service):
    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        pass

    def on_disconnect(self, conn):
        logging.info("Connection established with %s", conn)
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_announce(self, name):
        logging.info("Connection established with %s", name)

    def exposed_push_data(self, name, data):
        self.plugin_datas[name] = data
        
    def exposed_get_data(self, pluginName):
        try:
            return self.plugin_datas[pluginName]
        except KeyError:
            return None

    def exposed_send_fps(self, name, fps):
        self.fps_datas[name] = fps
        print(f"fps values: {self.fps_datas}", end="\r")

    plugin_datas = {}
    fps_datas = {}


    
def run():
    # Remove the log file if it exists
    if os.path.exists("ETS2LAInternalService.log"):
        os.remove("ETS2LAInternalService.log")
    # Create a custom logger so that we can save the output to a file, but we don't want to print it to the console.
    logger = logging.Logger("ETS2LAInternalService")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler("ETS2LAInternalService.log")
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    # Enable pickling for numpy etc...
    config = {'allow_pickle': True}

    t = ThreadedServer(ETS2LAInternalService, port=37521, logger=logger, protocol_config=config)
    threading.Thread(target=t.start, daemon=True).start()
    logging.info("Internal service started on port 37521")