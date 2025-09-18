from ETS2LA.Settings import ETS2LASettings
from typing import Literal


class Settings(ETS2LASettings):
    InternalVisualisation: bool = False
    ComputeSteeringData: bool = True
    SectorSize: int = 300
    LoadDistance: int = 600
    RoadQualityMultiplier: float = 1.0
    UseNavigation: bool = True
    DriveBasedOnTrailer: bool = True
    SendElevationData: bool = False
    ExportRoadOffsets: bool = False
    DisableFPSNotices: bool = False
    OverrideLaneOffsets: bool = False
    SteeringSmoothTime: float = 0.2
    downloaded_data: str | None = None
    selected_data: str | None = None
    UseAutoOffsetData: bool = False
    traffic_side: Literal["Right Handed", "Left Handed"] = "Right Handed"
    AutoTolls: bool = True


settings = Settings("Map")
