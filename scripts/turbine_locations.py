import glaes as gl
import pandas as pd
import numpy as np

def turbine_placement(input_path = 'glaes/test/data/de_1km.shp', output_path='test'):
    ec = gl.ExclusionCalculator(input_path, srs=3035, pixelSize=100, limitOne=False)
    
    ##### exclusions #####

    # Areas above the alpine forest line 
    ec.excludePrior("elevation_threshold", value=(1750, None) ) # alpine forest line assumed at 1750 m

    # maximum slope (degrees) and sea
    ec.excludePrior("slope_threshold", value=(11.3, None) )

    # "water bodies"
    ec.excludePrior("river_proximity", value=100 )

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

    # "power grid( >110kV) - 250m buffer"
    ec.excludePrior("power_line_proximity", value=(None, 250) )

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
    
    # visulisaton (currenly disabled)
    #ec.draw()
    
    # map of available area (currently not used)
    #ec.save("DE_land_availability.tif", overwrite=True)

    # Save turbine placement
    np.save(output_path, turbine_coordinates)