import rpyc
from rpyc.utils.server import ThreadedServer
import threading
import logging

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
        self.exposed_plugin_datas[name] = data
        print(f"Pushed data from {name}: {data}")

    def exposed_get_answer(self): # this is an exposed method
        return 42

    exposed_plugin_datas = {}

    def get_question(self):  # while this method is not exposed
        return "what is the airspeed velocity of an unladen swallow?"
    
def run():
    # Create a custom logger so that we can save the output to a file, but we don't want to print it to the console.
    logger = logging.Logger("ETS2LAInternalService")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler("ETS2LAInternalService.log")
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    t = ThreadedServer(ETS2LAInternalService, port=37521, logger=logger)
    threading.Thread(target=t.start, daemon=True).start()
    logging.info("Internal service started on port 37521")