from ETS2LA.Plugin import *

class Plugin(ETS2LAPlugin):
    information = PluginDescription(
        name="TestPlugin",
        version="1.0",
        description="A test plugin",
        dependencies=[],
        compatible_os=["Windows", "Linux"],
        compatible_game=["ETS2", "ATS"],
        update_log={
            "0.1": "Initial release",
            "0.2": "Fixed some bugs",
            "1.0": "Added some features"
        }
    )
    
    def run(self):
        print("Hello, World!")