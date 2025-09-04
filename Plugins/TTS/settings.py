from ETS2LA.Settings import ETS2LASettings


class Settings(ETS2LASettings):
    provider: str = ""
    voice: str = ""
    test_mode: bool = False
    volume: float = 1
    speed: float = 1
    road_proximity_beep: bool = True


settings = Settings("TTS")
