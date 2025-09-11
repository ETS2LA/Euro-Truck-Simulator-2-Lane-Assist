from ETS2LA.Settings import ETS2LASettings


class Settings(ETS2LASettings):
    lookahead_time: float = 3
    announce_state: bool = True
    max_speed: float = 30  # km/h
    visualize: bool = False
    sensitivity: float = 0.15


settings = Settings("collisionavoidance")
