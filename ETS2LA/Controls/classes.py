from typing import Literal, Any
import ETS2LA.Events as Events

class ControlEvent():
    alias: str = "control_event"
    """
    This is the internal alias for this control event.
    It's what you use in your code.
    """
    
    name: str = "ControlEvent"
    """
    The name of this control event. This is what is used
    when binding the control event to a keybind.
    """
    
    description: str = "The plugin author has not provided a description."
    """
    The description of the control event. This is used
    to describe the control event in the UI.
    """
    
    type: Literal["button", "axis"] = "button"
    """
    The type of the control event. This affects how the control
    can be bound to as well as how it's handled internally.
    """
    
    default: str = "k"
    """
    The default keyboard key for the control event.
    """
    
    __state: Any = None
    """
    Internal state. This is set by the plugin runner to
    update the control events from the main thread.
    """
    
    __last_state: Any = None
    """
    Internal last state. This is used to check if the
    control event has been triggered over the past frame.
    """

    def __init__(self, alias: str, name: str, type: Literal["button", "axis"], 
                 description: str = "", default: str = "", update_rate: float = 0.1):
        """
        Create a new ControlEvent.
        
        :param str alias: The internal alias for this control event.
        :param str name: The name of this control event.
        :param Literal["button", "axis"] type: The type of the control event.
        :param str description: The description of the control event.
        :param str default: The default keyboard key for the control event.
        :param float update_rate: The rate in seconds at which the backend will send the control data to this plugin.
        """
        self.alias = alias
        self.name = name
        self.type = type
        self.description = description
        self.default = default
        self.update_rate = update_rate
        
    def update(self, state: Any) -> None:
        """
        Refresh the controls and send out events if
        any of the control events have been triggered.
        """
        self.__last_state = self.__state
        self.__state = state
        
        if self.__last_state != self.__state:
            Events.events.emit(self.alias, state, queue=False)

        
    def pressed(self) -> Any:
        """
        Get the current boolean value of this ControlEvent.
        Only works for button type control events.
        """
        if not self.type == "button":
            raise ValueError("This control event is not a button type.")
        return self.__state

    
    def value(self) -> Any:
        """
        Get the current float value of this ControlEvent.
        Only works for axis type control events.
        """
        if not self.type == "axis":
            raise ValueError("This control event is not an axis type.")
        return self.__state