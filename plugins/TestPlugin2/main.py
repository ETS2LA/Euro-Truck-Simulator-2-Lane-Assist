from ETS2LA.Plugin import *
from ETS2LA.UI import *

"""
This is an example plugin file for the new ETS2LA plugin system.
You can use this as a template for your own plugins.
"""

VALUE = 0

class SettingsMenu(ETS2LASettingsMenu):
    dynamic = True # False means that the page is built once and then cached. True means that the page is rebuilt every time the frontend asks for an update.
    plugin_name = "TestPlugin2" # This will tell the settings menu where to save the settings
    def render(self):
        if self.settings.refresh_rate is None:
            self.settings.refresh_rate = 1
            
        RefreshRate(1/self.settings.refresh_rate)
        
        Title("Test Plugin")
        Description("Laborum sit enim laboris non et culpa. Quis ad sunt deserunt aute elit ut do tempor consequat Lorem laboris mollit commodo. Ad ullamco do in ex excepteur anim cillum non reprehenderit labore sunt aliquip. Sunt nisi ea ea voluptate ea commodo esse ullamco. Exercitation Lorem ea velit quis aliquip dolore. Laborum mollit qui minim commodo id magna minim esse ea nostrud dolor.")    
        
        Separator()
        
        with EnabledLock():
            Slider("Refresh rate", "refresh_rate", 1, 1, 30, 1, 
                   description="NOTE: This affects the UI only when the plugin is enabled!", 
                   suffix=" fps"
            )
            Button("Test!", "Test Button", Plugin.function)
        
        Space(4)
        Label("Live data from the plugin:")
        
        with EnabledLock():
            ProgressBar(VALUE % 4, 0, 4, 
                        description=f"Loading... ({round(VALUE % 4 / 4 * 100)}%)"
            )
            Slider("Print the value this many times", "slider", 4, 0, 10, 1)
            
            with Group("vertical"):
                if self.settings.slider is None:
                    self.settings.slider = 3
                for i in range(self.settings.slider):
                    Description(f"The value is {VALUE}")
                
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
    
    settings_menu = SettingsMenu()
    
    def function(self):
        print("Button clicked!")
    
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
        global VALUE
        VALUE = time.time()