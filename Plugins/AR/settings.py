from ETS2LA.Settings import ETS2LASettings


class Settings(ETS2LASettings):
    vision_compat: bool = False
    test_objects: bool = False
    show_when_not_in_focus: bool = False
    perf_overlay: bool = False
    game_stats: bool = False
    background: bool = True


settings = Settings("AR")
