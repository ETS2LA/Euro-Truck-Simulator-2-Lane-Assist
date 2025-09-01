from ETS2LA.Controls import ControlEvent
from ETS2LA.Utils.translator import _

enable_disable = ControlEvent(
    "toggle_acc",
    _("Toggle Speed Control"),
    "button",
    description=_("When ACC is running this will toggle the speed control on/off."),
    default="n",
)

increment = ControlEvent(
    "increment_speed",
    _("Increase Driving Speed Offset"),
    "button",
    description=_("This will increase the speed offset in the settings."),
    default="↑",
)

decrement = ControlEvent(
    "decrement_speed",
    _("Decrease Driving Speed Offset"),
    "button",
    description=_("This will decrease the speed offset in the settings."),
    default="↓",
)
