from ETS2LA.Plugin import ETS2LAPlugin
import logging

class ETS2LAModule:
    plugin: ETS2LAPlugin
    """
    Access to the plugin instance this module is bound to.
    
    Example:
    ```python
    value = self.plugin.settings.key
    module = self.plugin.modules.module_name
    ```
    """
    
    def ensure_functions(self) -> None:
        if "run" not in dir(type(self)):
            raise TypeError("Your module has to have a 'run' function.")
        if "imports" not in dir(type(self)):
            raise TypeError("Your module has to have an 'imports' function.")
        if type(self).__name__ != "Module":
            raise TypeError("Please make sure the class is named 'Module'")
        
    def __init__(self, plugin: object) -> None:
        self.ensure_functions()
        self.plugin = plugin
        self.imports()
        
        try: self.init()
        except Exception as ex:
            if type(ex) != AttributeError: 
                logging.exception("Error in 'init' function")
        try: self.initialize()
        except Exception as ex:
            if type(ex) != AttributeError: 
                logging.exception("Error in 'initialize' function")
        try: self.Initialize()
        except Exception as ex:
            if type(ex) != AttributeError: 
                logging.exception("Error in 'Initialize' function")