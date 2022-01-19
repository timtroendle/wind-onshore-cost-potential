import argparse

import glaes as gl
#from glaes.core.priors import PriorSet
import pandas as pd
import numpy as np


def turbine_placement(input_path, prior_directory_path, output_path_csv, output_path_tif):
    gl.Priors.loadDirectory(prior_directory_path)

    ec = gl.ExclusionCalculator(input_path, srs=3035, pixelSize=100, limitOne=False)

    ##### exclusions #####

    # Areas above the alpine forest line
    ec.excludePrior("elevation_threshold", value=(1750, None) ) # alpine forest line assumed at 1750 m

    # maximum slope (degrees) and sea
    ec.excludePrior("slope_threshold", value=(11.3, None) )

    # "water bodies"
    ec.excludePrior("river_proximity", value=(100, None) )

    # "settlement areas - 200m buffer"
    ec.excludePrior("settlement_proximity", value=(None, 200) )

    # "built up areas - 300m buffer"
    # "  * industrial, commercial, and mining areas"
    ec.excludePrior("industrial_proximity", value=(None, 300) )
    ec.excludePrior("mining_proximity", value=(None, 300) )

    # "railways - 300m buffer"
    ec.excludePrior("railway_proximity", value=(None, 300) )

    # "motorways, primary, and secondary roads - 300m buffer"
    ec.excludePrior("roads_main_proximity", value=(None, 300) )
    ec.excludePrior("roads_secondary_proximity", value=(None, 300) )

    # "airport public safety zones - 5100m buffer"
    ec.excludePrior("airport_proximity", value=(None, 5100) )

    # "power grid( >110kV) - 200m buffer"
    ec.excludePrior("power_line_proximity", value=(None, 200) )

    # "national parks - 1000m buffer"
    ec.excludePrior("protected_park_proximity", value=(None,1000) )

    # "Natura 2000 - habitats directive sites"
    # "*potentially"
    ec.excludePrior("protected_habitat_proximity", value=(None, 0) )

    # "Natura 2000 - birds directive sites"
    ec.excludePrior("protected_bird_proximity", value=(None, 0) )

    # "Other protected areas"
    # "*Biosphere reserves, landscape protection areas, natural monuments and sites,
    #   protected habitats, and landscape section"
    ec.excludePrior("protected_biosphere_proximity", value=(None, 0) )
    ec.excludePrior("protected_landscape_proximity", value=(None, 0) )
    ec.excludePrior("protected_natural_monument_proximity", value=(None, 0) )

    # "lakes (> 50 ha) - 1000m buffer"
    ec.excludePrior("lake_proximity", value=(None,1000) )

    #turbine placement
    ec.distributeItems(separation=1000)
    turbine_coordinates = ec.itemCoords

    #Advanced placement (not implemented)
    #ec.distributeItems(separation=(1200,600), axialDirection=45)

    # map of available area (currently not used)
    ec.save(output_path_tif, overwrite=True)

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
    parser.add_argument("output_path_csv", type=str)
    parser.add_argument("output_path_tif", type=str)

    turbine_placement(
        **vars(parser.parse_args())
    )
