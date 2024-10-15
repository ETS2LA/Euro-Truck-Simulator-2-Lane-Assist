from ETS2LA.Plugin import *
from ETS2LA.UI import *

"""
This is an example plugin file for the new ETS2LA plugin system.
You can use this as a template for your own plugins.
"""

class Settings(ETS2LASettingsMenu):
    dynamic = False # False means that the page is built once and then cached. True means that the page is rebuilt every time the frontend asks for an update.
    # NOTE: True is not yet implemented!
    def render(self):
        Title("Plugin Settings")
        Description("This is a description")
        
        Separator()
        Space(10)
        
        Label("This is a label")
        
        with Group(direction="horizontal", gap=4):
            Input("Test input", "test_input", "string", description="This is a test input")
            Input("Another input", "another_input", "number", description="This is another test input")
        
        Slider("Test slider", "test_slider", 0, 0, 100, 1, description="This is a test slider")
        Switch("Test switch", "test_switch", False, description="This is a test switch")
        
        with Group(direction="vertical", border=True):
            with Group(border=True):
                Toggle("Test toggle", "test_toggle", False, description="This is a test toggle")
                Toggle("Test toggle", "test_toggle", False, description="This is a test toggle")
                Toggle("Test toggle", "test_toggle", False, description="This is a test toggle")
            with Group():
                Toggle("Test toggle", "test_toggle", False, description="This is a test toggle", separator=False)
                Toggle("Test toggle", "test_toggle", False, description="This is a test toggle", separator=False)
                Toggle("Test toggle", "test_toggle", False, description="This is a test toggle", separator=False)
        
        Button("Wow!", "Do something cool!", Plugin.imports, description="Something is definitely bound to happen when you press this button")
        
        with TabView():
            with Tab(name="Tab 1"):
                Button("Wow!", "Do something cool!", Plugin.imports, description="This is on tab 1!", border=False)
            with Tab(name="Tab 2"):
                Button("Wow!", "Do something cool!", Plugin.imports, description="This on the other hand is the second tab!", border=False)
                
        return RenderUI()

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="TestPlugin2",
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
    
    settings_menu = Settings()
    
    def imports(self):
        """
        You should place all your (non ETS2LA) imports in this function. This is because during startup, 
        python has to read this file to get the information about the plugin.
        If you place large imports like torch outside of this function, it will drastically slow down 
        the entire startup process.

        NOTE: Some IDEs might not recognize imports here... so use vscode :)
        (looking at you PyCharm)
        """
        global json
        import json
    
    def run(self):
        #print(json.dumps(self.settings_menu.build(), indent=4))
        ...