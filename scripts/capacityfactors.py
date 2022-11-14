import argparse

import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import rioxarray # necessary for the rio accessor of DataArrays
from shapely.geometry import Point


DEPRECATED_GRID_SIZE_IN_M = 50000 # old style capacity factors are on a grid of 50km size

WGS84_EPSG = 4326
WGS84 = f"EPSG:{WGS84_EPSG}"
EPSG3035 = "EPSG:3035"


def preprocess_capacity_factors(path_to_raw_cf: str, path_to_output: str):
    ds = xr.open_dataset(path_to_raw_cf)
    ds = ds.mean("time") # ASSUME average over 17 years
    ds = ds.expand_dims(time=[1], axis=0) # re-add time dimension as function expects it
    da = convert_old_style_capacity_factor_time_series(ds)
    da = da.squeeze("timestep") # remove dummy time dimension
    da.rio.write_crs(EPSG3035, inplace=True)
    da.transpose('y', 'x').rio.to_raster(path_to_output)


def convert_old_style_capacity_factor_time_series(ts):
    """DEPRECATED: Converts published capacity factor data to new format.

    Existing capacity factor time series that are used in this workflow are published here:
    https://zenodo.org/record/3899687

    The old format is integer-indexed so that the integer refers to the location. `lat` and `lon`
    are variables of this dataset (they should be part of the index, but are not). In addition,
    while the data have been created by forming an equally-spaced grid on a projected plane
    (EPSG:3035), the data themselves are given in WGS84 and thus not on an equally-spaced grid.
    We will not use this format anymore in the future. Thus, we need to support it only as long
    as we did not update the published data.

    The new format is coordinate-indexed so that `timestep`, `x`, and `y` are the dimensions of
    the data. The disadvantage of this format is that it potentially includes a lot of `nans` in
    locations in which no data exist. As both netcdf4 and xarray support sparse datasets, this
    should not be a big disadvantage.

    This function takes data in the old format and converts them to the new format. The function is
    deprecated and should be removed as soon as the published data is updated with the new format.
    """
    site_id_map = {
        site_id.item(): (ts["lon"].sel(site_id=site_id).item(), ts["lat"].sel(site_id=site_id).item())
        for site_id in ts.site_id
    }
    gdf = (
        gpd
        .GeoDataFrame(
            data={"site_id": [site_id for site_id in site_id_map.keys()]},
            geometry=[Point(lon, lat) for lon, lat in site_id_map.values()],
            crs=WGS84
        )
        .set_index("site_id")
        .to_crs(EPSG3035)
    )
    gdf["x"] = [round(point.coords[0][0], ndigits=0) for point in gdf.geometry] # round to meter
    gdf["y"] = [round(point.coords[0][1], ndigits=0) for point in gdf.geometry] # round to meter
    ts["x"] = gdf["x"]
    ts["y"] = gdf["y"]
    ts = ts.set_index(site_id=["x", "y"]).unstack("site_id")
    ts = ts["electricity"].rename(time="timestep")

    # make sure the resolution is uniform
    x = ts.x
    y = ts.y
    assert ((x.diff("x") == DEPRECATED_GRID_SIZE_IN_M).sum() / x.count()).item() > 0.9 # most are fine
    assert ((y.diff("y") == DEPRECATED_GRID_SIZE_IN_M).sum() / x.count()).item() > 0.9 # most are fine
    ts = ts.reindex(
        x=np.arange(x[0], x[-1] + 1, step=DEPRECATED_GRID_SIZE_IN_M),
        y=np.arange(y[0], y[-1] + 1, step=DEPRECATED_GRID_SIZE_IN_M)
    )
    ts.attrs["crs"] = EPSG3035
    return ts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_raw_cf", type=str)
    parser.add_argument("path_to_output", type=str)

    preprocess_capacity_factors(
        **vars(parser.parse_args())
    )
