from typing import Literal, Any
import ETS2LA.Events as Events


class ControlEvent:
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

    plugin: str = ""
    """
    The plugin this control event belongs to. This is used to sort
    on the UI side.
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

    def __init__(
        self,
        alias: str,
        name: str,
        type: Literal["button", "axis"],
        description: str = "",
        default: str = "",
        plugin: str = "",
    ):
        """Create a new ControlEvent.

        :param str alias: The internal alias for this control event.
        :param str name: The name of this control event.
        :param Literal["button", "axis"] type: The type of the control event.
        :param str description: The description of the control event.
        :param str default: The default keyboard key for the control event.
        """
        self.alias = alias
        self.name = name
        self.type = type
        self.description = description
        self.default = default
        self.plugin = plugin

    def update(self, state: Any) -> None:
        """Refresh the controls and send out events if
        any of the control events have been triggered.
        """
        self.__last_state = self.__state
        self.__state = state

        if self.__last_state != self.__state:
            if self.type == "button":
                Events.events.emit(self.alias, self.pressed(), queue=False)
            elif self.type == "axis":
                Events.events.emit(self.alias, self.value(), queue=False)

    def pressed(self) -> Any:
        """Get the current boolean value of this ControlEvent.
        Only works for button type control events.
        """
        if not self.type == "button":
            raise ValueError("This control event is not a button type.")

        if self.__state is None:
            return False

        return bool(self.__state)

    def value(self) -> Any:
        """Get the current float value of this ControlEvent.
        Only works for axis type control events.
        """
        if not self.type == "axis":
            raise ValueError("This control event is not an axis type.")

        if self.__state is None:
            return 0.0

        return self.__state
