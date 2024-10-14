from ETS2LA.Plugin import *

"""
This is an example plugin file for the new ETS2LA plugin system.
You can use this as a template for your own plugins.
"""

class Plugin(ETS2LAPlugin):
    
    description = PluginDescription(
        name="TestPlugin3",
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

    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066"
    )
    
    def imports(self):
        """
        You should place all your (non ETS2LA) imports in this function. This is because during startup, 
        python has to read this file to get the information about the plugin.
        If you place large imports like torch outside of this function, it will drastically slow down 
        the entire startup process.

        NOTE: Some IDEs might not recognize imports here... so use vscode :)
        (looking at you PyCharm)
        """
        global time
        import time
    
    def run(self):
        self.globals.tags.test = "dd"