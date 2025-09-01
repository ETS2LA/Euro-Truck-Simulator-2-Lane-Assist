# Based on package/libs/map/projections.ts by truckermudgeon
# later forked to ETS2LA/maps

from pyproj import CRS, Transformer
import math

earth_radius = 6_370_997  # meters
length_of_degree = (earth_radius * math.pi) / 180.0

# ATS Projection
ats_projection = (
    f"+proj=lcc "
    f"+units=m +R={earth_radius} "
    f"+lat_1={33} +lat_2={45} "
    f"+lat_0={39} +lon_0={-96} "
)
ats_crs = CRS.from_proj4(ats_projection)
ats_transformer = Transformer.from_crs(ats_crs, CRS("EPSG:4326"))
ats_map_factor = [-0.00017706234, 0.000176689948]
ats_map_offset = [-5, 0]

# ETS2 Projection
ets2_projection = (
    f"+proj=lcc "
    f"+units=m +R={earth_radius} "
    f"+lat_1={37} +lat_2={65} "
    f"+lat_0={50} +lon_0={15} "
)
ets2_crs = CRS.from_proj4(ets2_projection)
ets2_transformer = Transformer.from_crs(ets2_crs, CRS("EPSG:4326"))
ets2_map_factor = [-0.000171570875, 0.0001729241463]
ets2_map_offset = [16660, 4150]


def get_ats_coordinates(x, y):
    x -= ats_map_offset[0]
    y -= ats_map_offset[1]

    proj_x = x * ats_map_factor[1] * length_of_degree
    proj_y = y * ats_map_factor[0] * length_of_degree
    lon, lat = ats_transformer.transform(proj_x, proj_y)
    return (lat, lon)


def get_ets2_coordinates(x, y):
    x -= ets2_map_offset[0]
    y -= ets2_map_offset[1]

    # UK has a different scale to the rest of the map
    uk_factor = 0.75
    # Consider everything to the north west of Calais as the UK
    calais = [-31100, -5500]
    is_uk = (x * uk_factor) < calais[0] and (y * uk_factor) < calais[1]
    if is_uk:
        x = (x + calais[0] / 2) * uk_factor
        y = (y + calais[1] / 2) * uk_factor

    proj_x = x * ets2_map_factor[1] * length_of_degree
    proj_y = y * ets2_map_factor[0] * length_of_degree
    lon, lat = ets2_transformer.transform(proj_x, proj_y)
    return (lat, lon)
