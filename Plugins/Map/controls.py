from ETS2LA.Controls import ControlEvent
from ETS2LA.Utils.translator import _

enable_disable = ControlEvent(
    "toggle_map",
    _("Toggle Steering"),
    "button",
    description=_(
        "When the Map plugin is running, this will toggle the steering on/off."
    ),
    default="n",
)
