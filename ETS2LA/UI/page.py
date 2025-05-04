from ETS2LA.UI import *
import time

class ETS2LAPage:
    """This is a base class for all ETS2LA pages.

    :param dynamic: If the page is dynamic, it will be rebuilt every time the frontend updates it.
    :param settings_target: The path to the settings file that the page will use.
    :param url: The relative URL of the page. (eg. /settings/global)
    :param refresh_rate: The refresh rate of the page in seconds. (0 = no limit)
    :param plugin: A reference to the plugin that spawned this page.
    :param settings: A reference to the settings object of the plugin that spawned this page.
    """
    
    url: str = ""
    last_update_: float = 0
    refresh_rate: int = 0
    
    plugin: object = None
    """
    A reference to the plugin that spawned this page.
    If the plugin is disabled, then this object will be None.
    """
    settings: object = None
    """
    A reference to the settings object of the plugin that spawned this page.
    If the plugin is disabled, then this object will be None.
    """
    
    def __init__(self):
        if "render" not in dir(type(self)):
            raise TypeError("Your page has to have a 'render' method.")
        if self.url == "":
            raise TypeError("You must set the 'url' variable to the relative URL of the page.")
        self._json = {}
        try:
            self.init() # type: ignore # Might or might not exist.
        except:
            pass
        
    def build(self):
        # Some pages might not need to be built every time.
        if self.refresh_rate != 0:
            if self.last_update_ + self.refresh_rate > time.perf_counter():
                return self._json
            
        RenderUI()  # Clear the UI system
        self.render() # type: ignore # Might or might not exist.
        self._json = RenderUI()
        self.last_update_ = time.perf_counter()
        
        return self._json