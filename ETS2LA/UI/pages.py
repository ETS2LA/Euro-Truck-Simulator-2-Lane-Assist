from ETS2LA.UI.components import ui, id
from ETS2LA.UI import *

class ETS2LAPage:
    """This is a base class for all ETS2LA pages.

    :param dynamic: If the page is dynamic, it will be rebuilt every time the frontend updates it.
    :param settings_target: The path to the settings file that the page will use.
    :param url: The relative URL of the page. (eg. /settings/global)
    """
    
    dynamic: bool = False
    settings_target: str = ""
    url: str = ""
    
    def __init__(self):
        if "render" not in dir(type(self)):
            raise TypeError("Your page has to have a 'render' method.")
        if self.settings_target == "":
            raise TypeError("You must set the 'settings_target' variable to the path of the settings file this page will use.")
        if self.url == "":
            raise TypeError("You must set the 'url' variable to the relative URL of the page.")
        self._json = {}
        
    def build(self):
        if self.dynamic:
            RenderUI()  # Clear the UI system
            ui = []
            id = []
            data = self.render()
            data.insert(0, {
                "settings": self.settings_target
            })
            return data
        
        if self._json == {}:
            RenderUI()  # Clear the UI system
            ui = []
            id = []
            self._json = self.render()
            self._json.insert(0, {
                "settings": self.settings_target
            })
        
        return self._json