import time
import logging
import rpyc
import os
import importlib

class PluginRunner():
    def __init__(self, pluginName):
        # Import the plugin
        module_name = "ETS2LA.plugins." + pluginName + ".main"
        self.plugin = importlib.import_module(module_name)
        self.plugin_name = self.plugin.PluginInfo.name
        logging.info(f"PluginRunner: Plugin {self.plugin_name} initialized")
        rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True # Enable pickling for numpy etc...
        self.server = rpyc.connect("localhost", 37521)
        self.server.root.exposed_announce(self.plugin_name)
        self.run()

    def run(self):
        while True:
            startTime = time.time()
            data = self.plugin.plugin(self)
            self.server.root.exposed_push_data(self.plugin_name, data)
            endTime = time.time()
            try:
                print(f"{self.plugin_name} fps = {1/(endTime-startTime)}")
            except:
                pass
                
    def GetData(self, pluginName):
        startTime = time.time()
        data = self.server.root.exposed_get_data(pluginName)
        if data is not None:
            data = data
            endTime = time.time()
            return data
        else:
            return None