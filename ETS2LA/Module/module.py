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

    def __init__(self, plugin: ETS2LAPlugin) -> None:
        self.ensure_functions()
        self.plugin = plugin
        self.imports()  # type: ignore # Might or might not exist.

        try:
            self.init()  # type: ignore # Might or might not exist.
        except Exception as ex:
            if not isinstance(ex, AttributeError):
                logging.exception("Error in 'init' function")
        try:
            self.initialize()  # type: ignore # Might or might not exist.
        except Exception as ex:
            if not isinstance(ex, AttributeError):
                logging.exception("Error in 'initialize' function")
        try:
            self.Initialize()  # type: ignore # Might or might not exist.
        except Exception as ex:
            if not isinstance(ex, AttributeError):
                logging.exception("Error in 'Initialize' function")
