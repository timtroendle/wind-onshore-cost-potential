"""Generates a single shape file per country from individual NUTS shapes"""

import argparse

from shapely.geometry import box
import geopandas as gpd


def isolate_country_shape(path_to_nuts, country_id, x_min, x_max, y_min, y_max, path_to_output):
    # As GLAES requires single polygons, we are isolating countries here.
    shape = (
        gpd
        .read_file(path_to_nuts)
        .set_index("NUTS_ID")
        .loc[[country_id], :]
    )
    continental_europe = box(x_min, y_min, x_max, y_max)
    (
        gpd
        .clip(shape, continental_europe)
        .to_file(path_to_output)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_nuts", type=str)
    parser.add_argument("country_id", type=str)
    parser.add_argument("x_min", type=float)
    parser.add_argument("x_max", type=float)
    parser.add_argument("y_min", type=float)
    parser.add_argument("y_max", type=float)
    parser.add_argument("path_to_output", type=str)

    isolate_country_shape(
        **vars(parser.parse_args())
    )
