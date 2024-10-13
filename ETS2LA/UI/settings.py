class ETS2LASettingsMenu:
    def __init__(self):
        if "render" not in dir(type(self)):
            raise TypeError("Your page has to have a 'render' method.")
        self._json = {}
        
    def build(self):
        if self._json == {}:
            self._json = self.render()
        return self._json