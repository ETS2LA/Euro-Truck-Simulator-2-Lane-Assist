from ETS2LA.UI import ETS2LAPage, ETS2LAPageLocation
from ETS2LA.UI import (
    TitleAndDescription,
    SliderWithTitleDescription,
    CheckboxWithTitleDescription,
    Text,
    styles,
)
from ETS2LA.Utils.translator import _

from Plugins.CollisionAvoidance.settings import settings


class SettingsPage(ETS2LAPage):
    title = _("Collision Avoidance")
    url = "/settings/collisionavoidance"
    location = ETS2LAPageLocation.SETTINGS
    refresh_rate = -1

    def handle_sensitivity(self, value: float):
        settings.sensitivity = value

    def handle_max_speed(self, value: float):
        settings.max_speed = value

    def handle_lookahead_time(self, value: float):
        settings.lookahead_time = value

    def handle_announce_state(self, *args):
        if args:
            settings.announce_state = args[0]
        else:
            settings.announce_state = not settings.announce_state

    def render(self):
        TitleAndDescription(
            _("Collision Avoidance"),
            _(
                "These settings will affect how ETS2LA reacts to traffic around it. Please note that this does not affect lane changes."
            ),
        )

        Text(
            _("[Experimental]"),
            styles.Classname("font-bold text-muted-foreground"),
        )

        SliderWithTitleDescription(
            title=_("Sensitivity"),
            description=_(
                "How close a vehicle has to be to the truck's path to be considered a threat. Higher values make the system more sensitive."
            ),
            suffix="m",
            min=0.05,
            default=settings.sensitivity,
            max=0.5,
            step=0.01,
            changed=self.handle_sensitivity,
        )

        SliderWithTitleDescription(
            title=_("Max Speed"),
            description=_(
                "The maximum speed the truck can be going for collision avoidance to be active."
            ),
            suffix="km/h",
            min=10,
            default=settings.max_speed,
            max=50,
            step=1,
            changed=self.handle_max_speed,
        )

        SliderWithTitleDescription(
            title=_("Lookahead Time"),
            description=_("How far ahead the system looks for potential collisions."),
            # TRANSLATORS: This means seconds, basically 3s = 3 seconds
            suffix=_("s"),
            min=1,
            default=settings.lookahead_time,
            max=5,
            step=0.1,
            changed=self.handle_lookahead_time,
        )

        CheckboxWithTitleDescription(
            title=_("Announce State"),
            description=_(
                "Announce when collision avoidance is activated or deactivated."
            ),
            default=settings.announce_state,
            changed=self.handle_announce_state,
        )
