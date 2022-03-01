from typing import List, Tuple
import argparse

import pandas as pd
from file_management import tif_values
import xarray as xr
import rioxarray
import numpy as np


def get_locations(path_to_turbine_locations:str) -> List[Tuple]:
    df = pd.read_csv(path_to_turbine_locations)
    return list(zip(df['x_m'], df['y_m']))


def merge(path_to_turbine_locations: str, path_to_lcoe: str, path_to_annual_energy: str, path_to_disamenity_cost: str, path_to_output: str):
    locations = get_locations(path_to_turbine_locations)
    
    # Decomposes list of tuples in arry of x coordinates and arry of y coordinates; alternative to zip(*locations)
    xs, ys = np.array(locations).transpose() 
    
    df = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            arrays=[xs, ys],
            names=('x_m', 'y_m')))
    
    df['lcoe_eur_per_mwh'] = tif_values(path_to_lcoe, coordinates=locations)
    df['disamenity_cost_eur_per_mwh'] = [disamenity/energy for disamenity, energy in zip(
        tif_values(path_to_disamenity_cost, coordinates=locations),
        tif_values(path_to_annual_energy, coordinates=locations),
    )]
    
    df.reset_index(inplace=True)

    df.to_csv(path_to_output)
    

# def merge(path_to_turbine_locations: str, path_to_lcoe: str, path_to_annual_energy: str, path_to_disamenity_cost: str, path_to_output: str):
#     turbines = pd.read_csv(path_to_turbine_locations, index_col=0)
#     lcoe = rioxarray.open_rasterio(path_to_lcoe)
#     full_load_hours = rioxarray.open_rasterio(path_to_annual_energy)
#     disamenity_cost = rioxarray.open_rasterio(path_to_disamenity_cost)
#     assert_same_coords(lcoe, disamenity_cost)
# 
#     disamenity_cost_per_mwh = disamenity_cost / full_load_hours
# 
#     x_res = int(lcoe.x.diff("x")[0].item()) // 2
#     y_res = int(lcoe.y.diff("y")[0].item()) // 2
# 
#     map_coords = turbines.apply(
#         lambda row: infer_map_coords(lcoe, x=row.x_m, y=row.y_m, x_res=x_res, y_res=y_res),
#         result_type="expand",
#         axis=1
#     )
#     lcoes = map_coords.apply(lambda row: lcoe.sel(x=row.x, y=row.y).item(), axis=1)
#     disamenity_costs = map_coords.apply(lambda row: disamenity_cost_per_mwh.sel(x=row.x, y=row.y).item(), axis=1)
#     (
#         turbines
#         .assign(lcoe_eur_per_mwh=lcoes, disamenity_cost_eur_per_mwh=disamenity_costs)
#         .to_csv(path_to_output, index=True, header=True)
#     )


def infer_map_coords(map: xr.DataArray, x: int, y: int, x_res: int, y_res: int): # TODO move to Python 3.9 to improve type hints
    """Returns map coordinates closest to input coordinates."""
    x_proximity = map.x.loc[slice(x - x_res, x + x_res)]
    y_proximity = map.y.loc[slice(y - y_res, y + y_res)]
    try:
        map_x = x_proximity.item()
    except ValueError:
        # handle case where x is equally far from two map points
        assert x_proximity.count() == 2, f"Exactly 2 values expected in proximity of {x}. Check resolution: {x_proximity}"
        map_x = x_proximity.values[0] # always take the smaller of the two
    try:
        map_y = y_proximity.item()
    except ValueError:
        # handle case where y is equally far from two map points
        assert y_proximity.count() == 2, f"Exactly 2 values expected in proximity of {y}. Check resolution: {y_proximity}"
        map_y = y_proximity.values[0] # always take the smaller of the two
    return {"x": map_x, "y": map_y}


def assert_same_coords(da1: xr.DataArray, da2: xr.DataArray):
    assert da1.spatial_ref.crs_wkt == da2.spatial_ref.crs_wkt
    assert len(da1.x) == len(da2.x)
    assert len(da2.y) == len(da2.y)
    assert da1.spatial_ref.GeoTransform == da2.spatial_ref.GeoTransform


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_turbine_locations", type=str)
    parser.add_argument("path_to_lcoe", type=str)
    parser.add_argument("path_to_annual_energy", type=str)
    parser.add_argument("path_to_disamenity_cost", type=str)
    parser.add_argument("path_to_output", type=str)

    merge(
        **vars(parser.parse_args())
    )
