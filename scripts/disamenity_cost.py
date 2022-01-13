import numpy as np

def disamenity_costs(radius_from, radius_to, scenario = 'low') -> float:
    return NotImplementedError


def population_in_radius(radius_from, radius_to) -> np.ndarray:
    """Reads the corrisponding Tiff files, returns the matrix resulting from the subraction"""
    # Not sure what makes more sense in snakemake. Becasue if you pass the radius as distance,
    # you do not know the path of the corresponding file. And vice versa. 
    return NotImplementedError


def calculate_disamenity(destination_path, max_radius:int):

    result = None
    
    for radius in range(max_radius):

        radius_from = radius
        radius_to = radius + 1

        disamenity = disamenity_costs(radius_from=radius_from, radius_to=radius_to, scenario = 'low')
        
        population = population_in_radius(radius_from=radius_from, radius_to=radius_to) 
        
        if result is None:
            result = population * disamenity
        else:
            result += population * disamenity # Check that this works with ndarray as expected...
        
        # TODO: Save the result in a new tif using the destination_path given as argument

