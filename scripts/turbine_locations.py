"""Uses the GLAES package and a set of exclusion criteria to generate a list of potential wind turbine locations"""

import argparse

import geokit as gk
import glaes as gl
import pandas as pd
import numpy as np


def turbine_placement(input_path: str, prior_directory_path: str, turbine_separation_m: int,
                      output_path_csv: str, output_path_tif: str):
    assert turbine_separation_m > 50 # value is in meters and must not be smaller than 50

    gl.Priors.loadDirectory(prior_directory_path)

    ec = gl.ExclusionCalculator(input_path, srs=3035, pixelSize=100, limitOne=False)

    # EXCLUSIONS BASED ON THRESHOLDS

    # areas above the alpine forest line
    ec.excludePrior("elevation_threshold", value=(1800, None))  # alpine forest line assumed at 1750 m

    # maximum slope (degrees) and sea
    ec.excludePrior("slope_threshold", value=(10, None))

    # EXCLUSIONS BASED ON PROXIMITY

    # lakes (> 50 ha)
    ec.excludePrior("lake_proximity", value=(None, 400))

    # other water bodies
    ec.excludePrior("river_proximity", value=(None, 200))

    # settlement areas
    ec.excludePrior("settlement_proximity", value=(None, 200))

    # industrial, commercial, and mining areas
    ec.excludePrior("industrial_proximity", value=(None, 300))
    ec.excludePrior("mining_proximity", value=(None, 100))

    # railways, motorways, primary and secondary roads
    ec.excludePrior("railway_proximity", value=(None, 150))
    ec.excludePrior("roads_main_proximity", value=(None, 200))
    ec.excludePrior("roads_secondary_proximity", value=(None, 100))

    # airport public safety zones
    ec.excludePrior("airport_proximity", value=(None, 5000))

    # power grid (>110kV)
    ec.excludePrior("power_line_proximity", value=(None, 200))

    # national parks
    ec.excludePrior("protected_park_proximity", value=(None, 1000))

    # Natura 2000 - protected habitats and birds
    ec.excludePrior("protected_habitat_proximity", value=(None, 1500))
    ec.excludePrior("protected_bird_proximity", value=(None, 1500))

    ec.excludePrior("protected_reserve_proximity", value=(None, 500))

    # other protected areas (biosphere reserves, landscape protection areas, natural monuments)
    ec.excludePrior("protected_biosphere_proximity", value=(None, 300))
    ec.excludePrior("protected_landscape_proximity", value=(None, 500))
    ec.excludePrior("protected_natural_monument_proximity", value=(None, 1000))

    ec.excludePrior("protected_wilderness_proximity", value=(None, 1000))
    

    #turbine placement
    ec.distributeItems(separation=turbine_separation_m)
    turbine_coordinates = ec.itemCoords

    #Advanced placement (not implemented)
    #ec.distributeItems(separation=(1200,600), axialDirection=45)

    # map of available area (currently not used)
    ec.save(output_path_tif, overwrite=True)

    if ec.srs.IsSame(gk.srs.EPSG3035) == 1: # this should always be the case in our analysis
        # EPSG3035's unit is meters, and sub-meter precision is not necessary.
        turbine_coordinates = turbine_coordinates.astype(int)
    # Save turbine placement
    (
        pd
        .DataFrame(turbine_coordinates)
        .rename(columns={0: "x_m", 1: "y_m"})
        .to_csv(output_path_csv, index=True, header=True)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str)
    parser.add_argument("prior_directory_path", type=str)
    parser.add_argument("turbine_separation_m", type=int)
    parser.add_argument("output_path_csv", type=str)
    parser.add_argument("output_path_tif", type=str)

    turbine_placement(
        **vars(parser.parse_args())
    )
