import time
import logging
import rpyc
import os
import importlib

class PluginRunner():
    def __init__(self, pluginName, logger):
        self.logger = logger
        self.enableTime = time.time()
        # Import the plugin
        module_name = "ETS2LA.plugins." + pluginName + ".main"
        self.plugin = importlib.import_module(module_name)
        self.plugin_name = self.plugin.PluginInfo.name
        self.logger.info(f"PluginRunner: Plugin {self.plugin_name} initialized")
        # Connect to the app server
        rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True # Enable pickling for numpy etc...
        self.server = rpyc.connect("localhost", 37521)
        self.server.root.exposed_announce(self.plugin_name)
        # Run the plugin
        self.run()

    def run(self):
        self.timer = time.time()
        while True:
            startTime = time.time()
            data = self.plugin.plugin(self)
            self.server.root.exposed_push_data(self.plugin_name, data)
            endTime = time.time()
            if endTime - self.timer > 1:
                self.server.root.exposed_send_fps(self.plugin_name, 1 / (endTime - startTime))
                self.timer = endTime
                
    def GetData(self, pluginName):
        data = self.server.root.exposed_get_data(pluginName)
        if data is not None:
            return data
        else:
            return None