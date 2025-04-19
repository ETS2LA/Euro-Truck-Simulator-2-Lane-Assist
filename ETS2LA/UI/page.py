from ETS2LA.UI import *
import time

class ETS2LAPage:
    """This is a base class for all ETS2LA pages.

    :param dynamic: If the page is dynamic, it will be rebuilt every time the frontend updates it.
    :param settings_target: The path to the settings file that the page will use.
    :param url: The relative URL of the page. (eg. /settings/global)
    """
    
    url: str = ""
    refresh_rate: int = 1
    last_update_: float = 0
    
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
        if time.perf_counter() - self.last_update_ < self.refresh_rate and self._json != {}:
            return self._json
        
        RenderUI()  # Clear the UI system
        self.render() # type: ignore # Might or might not exist.
        self._json = RenderUI()
        self.last_update_ = time.perf_counter()
        
        return self._json