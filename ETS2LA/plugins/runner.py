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
        self.server = rpyc.connect("localhost", 37521)
        self.server.root.exposed_announce(self.plugin_name)
        self.run()

    def run(self):
        while True:
            data = self.plugin.plugin()
            time.sleep(0.001)
            if data != None:
                self.server.root.exposed_push_data(self.plugin_name, data)