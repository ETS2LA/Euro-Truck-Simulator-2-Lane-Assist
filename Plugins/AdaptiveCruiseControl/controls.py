from ETS2LA.Controls import ControlEvent

enable_disable = ControlEvent(
    "toggle_acc",
    "Toggle Adaptive Cruise Control",
    "button",
    description="When ACC is running this will toggle it on/off.",
    default="n"
)

increment = ControlEvent(
    "increment_speed",
    "Increase Speed Offset",
    "button",
    description="This will decrease the speed offset in the settings.",
    default="↑"
)

decrement = ControlEvent(
    "decrement_speed",
    "Decrease Speed Offset",
    "button",
    description="This will increase the speed offset in the settings.",
    default="↓"
)