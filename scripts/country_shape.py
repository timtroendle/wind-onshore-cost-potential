import argparse

import geopandas as gpd


def isolate_country_shape(path_to_nuts, country_id, path_to_output):
    # As GLAES requires single polygons, we are isolating countries here.
    shape = (
        gpd
        .read_file(path_to_nuts)
        .set_index("NUTS_ID")
        .loc[[country_id], :]
    )

    shape.to_file(path_to_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_nuts", type=str)
    parser.add_argument("country_id", type=str)
    parser.add_argument("path_to_output", type=str)

    isolate_country_shape(
        **vars(parser.parse_args())
    )
