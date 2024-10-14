class ETS2LASettingsMenu:
    """This is a base class for all settings pages.

    :param dynamic: If the page is dynamic, it will be rebuilt every time the frontend updates it.
    :raises TypeError: You must have a 'render' method in your settings class.
    """
    dynamic: bool = False
    def __init__(self):
        if "render" not in dir(type(self)):
            raise TypeError("Your page has to have a 'render' method.")
        self._json = {}
        
    def build(self):
        if self._json == {}:
            self._json = self.render()
        return self._json