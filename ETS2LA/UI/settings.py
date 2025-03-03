from ETS2LA.Plugin.settings import Settings

class ETS2LASettingsMenu:
    """This is a base class for all settings pages.

    :param dynamic: If the page is dynamic, it will be rebuilt every time the frontend updates it.
    :param plugin_name: The name of the plugin directory.
    :raises TypeError: You must have a 'render' method in your settings class.
    """
    dynamic: bool = False
    settings: Settings | None = None
    plugin_name: str = ""
    plugin: object = None
    
    def __init__(self):
        if "render" not in dir(type(self)):
            raise TypeError("Your page has to have a 'render' method.")
        self._json = {}
        if self.plugin_name != "":
            self.settings = Settings(f"plugins/{self.plugin_name}")
        else:
            raise TypeError("You must set the 'plugin_name' variable to the name of your plugin directory.")
        
    def build(self):
        if self.dynamic:
            return self.render() # type: ignore # Might or might not exist.
        
        if self._json == {}:
            self._json = self.render() # type: ignore # Might or might not exist.
        
        return self._json
    
    def call_function(self, name, args=[], kwargs={}):
        if hasattr(self, name):
            return getattr(self, name)(*args, **kwargs)
        return None