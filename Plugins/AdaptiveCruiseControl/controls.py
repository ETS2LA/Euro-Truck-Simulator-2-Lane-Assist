from ETS2LA.Controls import ControlEvent

enable_disable = ControlEvent(
    "toggle_acc",
    "Toggle Speed Control",
    "button",
    description="When ACC is running this will toggle it on/off.",
    default="n"
)

increment = ControlEvent(
    "increment_speed",
    "Increase Driving Speed Offset",
    "button",
    description="This will decrease the speed offset in the settings.",
    default="↑"
)

decrement = ControlEvent(
    "decrement_speed",
    "Decrease Driving Speed Offset",
    "button",
    description="This will increase the speed offset in the settings.",
    default="↓"
)