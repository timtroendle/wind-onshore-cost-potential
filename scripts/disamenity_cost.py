import rasterio
import numpy as np

from scripts.file_management import write_tif, tif_data, tif_transform


def disamenity_costs(radius_from, radius_to, scenario = 'low') -> float:
    # TODO: Anselm, could you add here the function stored somewhere in the notebook?!
    raise NotImplementedError


def calculate_disamenity(distances, source_paths, destination_path):
    
    # Create a list of tuples [(distance1, path1), ...]
    distance_path = [
        (distance, source_path)
        for distance, source_path in zip(distances, source_paths)]
    # Sort by distance, although it should not be necessary
    distance_path.sort(key=lambda tup: tup[0])
    
    for i in range(len(distance_path)):

        if i == 0:
            population = tif_data(distance_path[i][1]) # Fist element of the list (lowest distance), second [1] element of the tuple (path)
            disamenity = disamenity_costs(
                radius_from=0,
                radius_to=distance_path[i][0])

            transform = tif_transform(distance_path[i][1])
            result = population * disamenity

        else:
            population = tif_data(distance_path[i][1]) - tif_data(distance_path[i-1][1]) # Fist element of the list (lowest distance), second [1] element of the tuple (path) 
            disamenity = disamenity_costs(
                radius_from=distance_path[i-1][0],
                radius_to=distance_path[i-1][0])

            new_transform = tif_transform(distance_path[i][1])
            assert new_transform == transform, 'You are iterating over .tif files that have different affine transform matices'
            transform = new_transform

            result += population * disamenity

    write_tif(
        full_path=destination_path, 
        data=result, 
        transform=transform
    )


if __name__ == '__main__':
    
    calculate_disamenity(
        distances=snakemake.params.distances,               # This should be a list of distances
        source_paths=snakemake.input.population_in_radius,  # List corresponding (by position) to the population within radius (distance) 
        destination_path=snakemake.output.disamenity,       # Path used to save the disamenity tif file
    )
