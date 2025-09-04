from ETS2LA.Settings.classes import ETS2LASettings
from typing import Literal


class GlobalSettings(ETS2LASettings):
    # User interface
    language: str = "English"
    frameless: bool = True
    transparency: bool = False
    transparency_alpha: float = 0.8

    debug_mode: bool = False
    stay_on_top: bool = True
    snow: bool = True
    fireworks: bool = True

    window_position: tuple[int, int] = (0, 0)
    window_timeout: int = 10
    width: int = 1280
    height: int = 720

    frontend_port: int = 3005
    frontend_mirror: str = "Auto"
    theme: Literal["dark", "light"] = "dark"
    ad_preference: int = 1  # 0 = none, 1 = minimal, 2 = medium, 3 = full

    # Account
    user_id: str = ""
    token: str = ""

    # Backend
    use_fancy_traceback: bool = True
    acceleration_fallback: bool = True
    display: int = 0

    running_plugins: list[str] = []
    send_crash_reports: bool = True
    advanced_plugin_mode: bool = False
    slow_loading: bool = False
    high_priority: bool = True

    # Sounds
    soundpack: str = "default"
    volume: float = 50
    startup_sound: bool = True

    def __init__(self):
        super().__init__("global")
