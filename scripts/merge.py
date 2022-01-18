import argparse

import pandas as pd
import rioxarray


def merge(path_to_turbine_locations, path_to_lcoe, path_to_output):
    turbines = pd.read_csv(path_to_turbine_locations, index_col=0)
    lcoe = rioxarray.open_rasterio(path_to_lcoe)

    lcoes = turbines.apply(
        lambda row: lcoe_of_turbine(lcoe, x=row.x_m, y=row.y_m),
        axis=1
    )
    turbines.assign({"lcoe-eur-per-mwh": lcoes}).to_csv(path_to_output, index=True, header=True)


def lcoe_of_turbine(lcoe, x, y):
    """Returns LCOE closest to input coordinates."""
    lcoe_x = abs(lcoe.x - x).idxmin().item()
    lcoe_y = abs(lcoe.y - y).idxmin().item()
    return lcoe.sel(x=lcoe_x, y=lcoe_y).item()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_turbine_locations", type=str)
    parser.add_argument("path_to_lcoe", type=str)
    parser.add_argument("path_to_output", type=str)

    merge(
        **vars(parser.parse_args())
    )
