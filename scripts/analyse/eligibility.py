import argparse

import numpy as np
import rasterio

ROAD_PROXIMITY_LIST = [
    0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2250, 2500,
    2750, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000, 12000, 14000, 16000, 18000, 20000
] # copied from GLAES codebase
ROAD_PROXIMITY_MAP = {i: v for i, v in enumerate(ROAD_PROXIMITY_LIST)}
ROAD_PROXIMITY_MAP[254] = ROAD_PROXIMITY_LIST[-1]
ROAD_PROXIMITY_MAP[255] = np.nan

NOT_ELIGIBLE = 0
ELIGIBLE = 1
DATATYPE = np.uint8


def land_eligibility(path_to_road_proximity, path_to_output, min_road_distance_in_m):
    with rasterio.open(path_to_road_proximity) as src:
        transform = src.transform
        road_proximity = src.read(1)
        crs = src.crs
    road_proximity = from_index_to_value(road_proximity)
    eligibility = determine_eligibility(road_proximity, min_road_distance_in_m)
    with rasterio.open(path_to_output, 'w', driver='GTiff', height=eligibility.shape[0],
                       width=eligibility.shape[1], count=1, dtype=DATATYPE,
                       crs=crs, transform=transform) as new_geotiff:
        new_geotiff.write(eligibility, 1)


def from_index_to_value(road_proximity):
    return np.vectorize(lambda x: ROAD_PROXIMITY_MAP[x])(road_proximity)


def determine_eligibility(road_proximity, min_road_distance_in_m):
    eligibility = np.ones_like(road_proximity, dtype=DATATYPE) * NOT_ELIGIBLE
    eligibility[road_proximity > min_road_distance_in_m] = ELIGIBLE
    return eligibility


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_road_proximity", type=str)
    parser.add_argument("min_road_distance_in_m", type=int)
    parser.add_argument("path_to_output", type=str)

    land_eligibility(
        **vars(parser.parse_args())
    )
