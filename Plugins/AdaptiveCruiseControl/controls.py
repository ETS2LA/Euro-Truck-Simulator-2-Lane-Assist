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

increment_follow_dist = ControlEvent(
    "increment_follow_distance",
    "Increase Following Distance",
    "button",
    description="Increase the ACC following distance.",
    default="PageUp"
)

decrement_follow_dist = ControlEvent(
    "decrement_follow_distance",
    "Decrease Following Distance",
    "button",
    description="Decrease the ACC following distance.",
    default="PageDown"
)