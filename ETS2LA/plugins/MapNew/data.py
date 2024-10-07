from classes import MapData, Road, Prefab

# MARK: Variables
truck_rotation: float = 0
"""Truck rotation updated at the start of each map frame."""
truck_x: float = 0
"""Truck X position updated at the start of each map frame."""
truck_y: float = 0
"""Truck Y position updated at the start of each map frame."""
truck_z: float = 0
"""Truck Z position updated at the start of each map frame."""
current_sector_x: int = 0
"""The sector X coordinate corresponding to the truck's position."""
current_sector_y: int = 0
"""The sector Y coordinate corresponding to the truck's position."""


# MARK: Data variables
data: MapData = None
"""This includes all of the ETS2 data that can be accessed."""
current_sector_roads: list[Road] = []
"""The roads in the current sector."""
current_sector_prefabs: list[Prefab] = []
"""The prefabs in the current sector."""

# MARK: Helpers
heavy_calculations_this_frame: int = 0
"""How many heavy calculations map has done this frame."""
allowed_heavy_calculations: int = 50
"""How many heavy calculations map is allowed to do per frame."""