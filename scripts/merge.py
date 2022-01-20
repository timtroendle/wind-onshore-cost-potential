import argparse

import pandas as pd
import xarray as xr
import rioxarray


def merge(path_to_turbine_locations: str, path_to_lcoe: str, path_to_disamenity_cost: str, path_to_output: str):
    turbines = pd.read_csv(path_to_turbine_locations, index_col=0)[:100] # FIXME see https://github.com/timtroendle/wind-externalities/issues/5
    lcoe = rioxarray.open_rasterio(path_to_lcoe)
    disamenity_cost = rioxarray.open_rasterio(path_to_disamenity_cost)
    assert_same_coords(lcoe, disamenity_cost)

    map_coords = turbines.apply(
        lambda row: infer_map_coords(lcoe, x=row.x_m, y=row.y_m),
        result_type="expand",
        axis=1
    )
    lcoes = map_coords.apply(lambda row: lcoe.sel(x=row.x, y=row.y).item(), axis=1)
    disamenity_costs = map_coords.apply(lambda row: disamenity_cost.sel(x=row.x, y=row.y).item(), axis=1)
    (
        turbines
        .assign(lcoe_eur_per_mwh=lcoes, disamenity_cost_eur_per_turbine=disamenity_costs)
        .to_csv(path_to_output, index=True, header=True)
    )


def infer_map_coords(map: xr.DataArray, x: int, y: int): # TODO move to Python 3.9 to improve type hints
    """Returns map coordinates closest to input coordinates."""
    map_x = abs(map.x - x).idxmin().item()
    map_y = abs(map.y - y).idxmin().item()
    return {"x": map_x, "y": map_y}


def assert_same_coords(da1: xr.DataArray, da2: xr.DataArray):
    # assert da1.spatial_ref.crs_wkt == da2.spatial_ref.crs_wkt # FIXME fails due to https://github.com/timtroendle/wind-externalities/issues/7
    assert len(da1.x) == len(da2.x)
    assert len(da2.y) == len(da2.y)
    assert da1.spatial_ref.GeoTransform == da2.spatial_ref.GeoTransform


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_turbine_locations", type=str)
    parser.add_argument("path_to_lcoe", type=str)
    parser.add_argument("path_to_disamenity_cost", type=str)
    parser.add_argument("path_to_output", type=str)

    merge(
        **vars(parser.parse_args())
    )
