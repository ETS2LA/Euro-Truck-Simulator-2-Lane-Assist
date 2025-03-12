from ETS2LA.Controls import ControlEvent

enable_disable = ControlEvent(
    "toggle_acc",
    "Toggle Adaptive Cruise Control",
    "button",
    description="When ACC is running this will toggle it on/off.",
    default="n"
)