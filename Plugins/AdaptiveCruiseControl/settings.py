from ETS2LA.UI import (
    ETS2LAPage,
    ETS2LAPageLocation,
    styles,
    TitleAndDescription,
    Tabs,
    Tab,
    Container,
    ComboboxWithTitleDescription,
    CheckboxWithTitleDescription,
    SliderWithTitleDescription,
    InputWithTitleDescription,
    Text,
    Youtube,
)
from ETS2LA.Settings import ETS2LASettings
from ETS2LA.Utils.translator import _
from typing import Literal


class Settings(ETS2LASettings):
    MU: float = 0.5
    ignore_traffic_lights: bool = False
    aggressiveness: Literal["Eco", "Normal", "Aggressive"] = "Normal"
    following_distance: float = 2
    overwrite_speed: float = 30
    speed_offset_type: Literal["Percentage", "Absolute"] = "Absolute"
    speed_offset: float = 0
    ignore_speed_limit: bool = False
    unlock_pid: bool = False
    pid_kp: float = 0.30
    pid_ki: float = 0.08
    pid_kd: float = 0.05
    traffic_light_mode: Literal["Legacy", "Normal"] = "Normal"
    max_speed: float = 0


settings = Settings("AdaptiveCruiseControl")


class SettingsMenu(ETS2LAPage):
    url = "/settings/adaptivecruisecontrol"
    location = ETS2LAPageLocation.SETTINGS
    title = _("Adaptive Cruise Control")
    refresh_rate = -1

    def handle_aggressiveness(self, value):
        settings.aggressiveness = value

    def handle_following_distance(self, value):
        settings.following_distance = value

    def handle_ignore_traffic_lights(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.ignore_traffic_lights

        settings.ignore_traffic_lights = value

    def handle_speed_offset_type(self, value):
        settings.speed_offset_type = value
        settings.speed_offset = 0

    def handle_speed_offset(self, value):
        settings.speed_offset = value

    def handle_coefficient_of_friction(self, value):
        settings.MU = value

    def handle_max_speed(self, value):
        if isinstance(value, str):
            value = float(value)
        settings.max_speed = value

    def handle_overwrite_speed(self, value):
        if isinstance(value, str):
            value = float(value)
        settings.overwrite_speed = value

    def handle_ignore_speed_limit(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.ignore_speed_limit

        settings.ignore_speed_limit = value

    def handle_pid_unlock(self, *args):
        if args:
            value = args[0]
        else:
            value = not settings.unlock_pid

        settings.unlock_pid = value

    def handle_pid_kp(self, value):
        settings.pid_kp = value

    def handle_pid_ki(self, value):
        settings.pid_ki = value

    def handle_pid_kd(self, value):
        settings.pid_kd = value

    def handle_traffic_light_mode(self, value):
        settings.traffic_light_mode = value

    def render(self):
        TitleAndDescription(
            title=_("Adaptive Cruise Control"),
            description=_(
                "Adaptive Cruise Control (ACC) controls the speed of the truck based on information gathered from the game."
            ),
        )

        with Tabs():
            with Tab(
                _("Adaptive Cruise Control"),
                container_style=styles.FlexVertical() + styles.Gap("24px"),
            ):
                Text(_("ACC Settings"), styles.Classname("font-semibold"))
                ComboboxWithTitleDescription(
                    options=["Eco", "Normal", "Aggressive"],
                    default=settings.aggressiveness,
                    title=_("Aggressiveness"),
                    description=_(
                        "How aggressively should the ACC follow the car in front and change the speedlimit?"
                    ),
                    changed=self.handle_aggressiveness,
                )

                with Container(styles.FlexVertical() + styles.Gap("10px")):
                    follow_distance = settings.following_distance
                    if isinstance(follow_distance, str):
                        follow_distance = 2
                        settings.following_distance = follow_distance

                    SliderWithTitleDescription(
                        title=_("Follow Distance"),
                        description=_(
                            "How far should the ACC keep from the vehicle in front?"
                        ),
                        default=follow_distance,
                        min=0.5,
                        max=4,
                        step=0.1,
                        suffix=" seconds",
                        changed=self.handle_following_distance,
                    )

                    target_dist = follow_distance * (80 / 3.6)
                    target_dist_ft = target_dist * 3.28084
                    Text(
                        "-> "
                        + _(
                            "At 80km/h ETS2LA will keep approximately {distance}m ({distance_ft}ft) from the vehicle in front."
                        ).format(
                            distance=round(target_dist),
                            distance_ft=round(target_dist_ft),
                        ),
                        styles.Classname("text-xs text-muted-foreground"),
                    )

                Text(_("Traffic Light Settings"), styles.Classname("font-semibold"))

                ignore = settings.ignore_traffic_lights
                CheckboxWithTitleDescription(
                    title=_("Ignore Traffic Lights"),
                    description=_(
                        "Whether the ACC should ignore traffic lights. Please note that this will, as it says ignore the traffic lights."
                    ),
                    changed=self.handle_ignore_traffic_lights,
                    default=ignore,
                )

                if not ignore:
                    ComboboxWithTitleDescription(
                        options=["Legacy", "Normal"],
                        title=_("Traffic Light Mode"),
                        changed=self.handle_traffic_light_mode,
                        default=settings.traffic_light_mode,
                        description=_(
                            "Select how the ACC should handle traffic lights. Normal mode handles lights on the other side of the intersection better."
                        ),
                    )

            with Tab(
                _("Speed Control"),
                container_style=styles.FlexVertical() + styles.Gap("24px"),
            ):
                Text(_("Curve Settings"), styles.Classname("font-semibold"))
                SliderWithTitleDescription(
                    title=_("Coefficient of Friction"),
                    description=_(
                        "The coefficient of friction used for the ACC calculations. Higher values allow the truck to drive faster in curves."
                    ),
                    min=0.1,
                    max=1,
                    step=0.1,
                    default=settings.MU,
                    changed=self.handle_coefficient_of_friction,
                    suffix=" μ",
                )

                Text(_("Speed Limit Settings"), styles.Classname("font-semibold"))

                with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                    if settings.max_speed is None:
                        settings.max_speed = 0

                    try:
                        max_speed_mph = settings.max_speed * 0.6213712
                    except Exception:
                        max_speed_mph = 0

                    InputWithTitleDescription(
                        title=_("Maximum Speed"),
                        description=f"({max_speed_mph:.0f} mph) "
                        + _(
                            "The maximum speed ACC will drive at. Set this to 0 to disable."
                        ),
                        default=settings.max_speed,
                        changed=self.handle_max_speed,
                        type="number",
                    )

                    if settings.overwrite_speed is None:
                        settings.overwrite_speed = 30

                    try:
                        fallback_speed_mph = settings.overwrite_speed * 0.6213712
                    except Exception:
                        fallback_speed_mph = 0

                    InputWithTitleDescription(
                        title=_("Fallback speed"),
                        description=f"({fallback_speed_mph:.0f} mph) "
                        + _(
                            "The speed to drive when the game tells us that the speed limit is 0 km/h."
                        ),
                        default=settings.overwrite_speed,
                        changed=self.handle_overwrite_speed,
                        type="number",
                    )

                ignore_speed_limit = settings.ignore_speed_limit
                CheckboxWithTitleDescription(
                    title=_("Ignore Speed Limit"),
                    description=_("Whether the ACC should ignore the speed limit."),
                    changed=self.handle_ignore_speed_limit,
                    default=ignore_speed_limit,
                )

                if ignore_speed_limit is not True:
                    with Container(styles.FlexHorizontal() + styles.Gap("24px")):
                        speed_offset_type = settings.speed_offset_type
                        ComboboxWithTitleDescription(
                            options=["Percentage", "Absolute"],
                            default=speed_offset_type,
                            title=_("Speed Offset Type"),
                            changed=self.handle_speed_offset_type,
                            description=_("Select the type of speed offset to apply."),
                        )

                        SliderWithTitleDescription(
                            title=_("Speed Offset"),
                            description=_(
                                "The speed offset to apply to all speedlimits. Please note that you can also change this dynamically with the keybinds in the controls."
                            ),
                            min=-30,
                            max=30,
                            step=1,
                            default=settings.speed_offset,
                            changed=self.handle_speed_offset,
                            suffix="%" if speed_offset_type == "Percentage" else "km/h",
                        )

            with Tab(
                _("PID"), container_style=styles.FlexVertical() + styles.Gap("24px")
            ):
                unlocked = settings.unlock_pid
                CheckboxWithTitleDescription(
                    title=_("Unlock PID"),
                    description=_(
                        "You can unlock the PID settings to adjust them manually. This isn't recommended unless you know what a PID is and how you can tune it correctly."
                    ),
                    changed=self.handle_pid_unlock,
                    default=unlocked,
                )

                if unlocked:
                    SliderWithTitleDescription(
                        title=_("PID Kp"),
                        description=_(
                            "Are we there yet? No? Then we need to accelerate more! (Proportional gain for the PID controller.)"
                        ),
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        default=settings.pid_kp,
                        changed=self.handle_pid_kp,
                    )
                    SliderWithTitleDescription(
                        title=_("PID Ki"),
                        description=_(
                            "Has it been a while since we were there? Then we need to accelerate more! (Integral gain for the PID controller.)"
                        ),
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        default=settings.pid_ki,
                        changed=self.handle_pid_ki,
                    )
                    SliderWithTitleDescription(
                        title=_("PID Kd"),
                        description=_(
                            "How fast are we approaching the target? If we are approaching too fast, we need to decelerate more! (Derivative gain for the PID controller.)"
                        ),
                        min=0.01,
                        max=1.0,
                        step=0.01,
                        default=settings.pid_kd,
                        changed=self.handle_pid_kd,
                    )

                Text(
                    _(
                        "This video visually explains how a PID controller works. Please watch it fully if you are not familiar with them."
                    ),
                    style=styles.Description(),
                )
                with Container(
                    styles.FlexHorizontal()
                    + styles.Width("100%")
                    + styles.Height("400px")
                ):
                    Youtube("qKy98Cbcltw")
