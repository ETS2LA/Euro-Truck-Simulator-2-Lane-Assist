from ETS2LA.Settings import ETS2LASettings


class Settings(ETS2LASettings):
    offset_x: float = 0
    offset_y: float = 0
    offset_z: float = 0
    renderers: list[str] = []
    darkness: float = 0
    day_darkness: float = 0.2
    scale_height: bool = False
    widgets: list[str] = []
    widget_scaling: float = 1.0


settings = Settings("HUD")
