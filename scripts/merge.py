import argparse

import pandas as pd
import xarray as xr
import numpy as np

from typing import List, Tuple

from file_management import tif_values
from disamenity_cost import disamenity_costs


def get_locations(path_to_turbine_locations:str) -> List[Tuple]:
    df = pd.read_csv(path_to_turbine_locations)
    return list(zip(df['x_m'], df['y_m']))


def merge(
    distances: List[str],
    path_to_turbine_locations: str,
    path_to_lcoe: str,
    path_to_annual_energy: str,
    path_to_disamenity_cost: str,
    paths_to_population_by_distance: List[str],
    path_to_output: str
):

    locations = get_locations(path_to_turbine_locations)

    # Decomposes list of tuples in arry of x coordinates and arry of y coordinates; alternative to zip(*locations)
    xs, ys = np.array(locations).transpose()

    df = pd.DataFrame(
        index=pd.MultiIndex.from_arrays(
            arrays=[xs, ys],
            names=('x_m', 'y_m')))

    df['lcoe_eur_per_mwh'] = tif_values(path_to_lcoe, coordinates=locations)
    mw_per_turbine = 2
    df['disamenity_cost'] = tif_values(path_to_disamenity_cost, coordinates=locations)
    df['annual_energy'] = tif_values(path_to_annual_energy, coordinates=locations)
    df['disamenity_cost_eur_per_mwh'] = [disamenity/(energy*mw_per_turbine) for disamenity, energy in zip(
        tif_values(path_to_disamenity_cost, coordinates=locations),
        tif_values(path_to_annual_energy, coordinates=locations),
    )]

    previous_distance = None
    cumulated_population = 0
    cumulated_cost = 0
    for distance, path_to_population in zip(distances, paths_to_population_by_distance):

        # Population in a counted between two distances
        df[distance] = tif_values(path_to_population, coordinates=locations)
        if previous_distance is not None:
            df[distance] -= cumulated_population

            # Disamenity cost (for QA)
            df[f'cost_{distance}'] = df[distance] * disamenity_costs(previous_distance, distance)
        else:
            df[f'cost_{distance}'] = df[distance] * disamenity_costs(0.2, distance)

        cumulated_cost += df[f'cost_{distance}']
        cumulated_population += df[distance]
        previous_distance = distance

    df['cumulated_cost'] = cumulated_cost

    df.reset_index(inplace=True)

    df.to_csv(path_to_output)


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
    parser.add_argument("paths_to_population_by_distance", type=str, nargs="*")
    parser.add_argument("--distances", type=int, nargs="*")
    parser.add_argument("path_to_output", type=str)

    merge(
        **vars(parser.parse_args())
    )
