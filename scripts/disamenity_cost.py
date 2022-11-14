"""Generates raster files containg the total disamanity cost per cell"""

import argparse

import numpy as np

from file_management import write_tif, tif_data, tif_transform, tif_crs, tif_values


def disamenity_costs(radius_from, radius_to) -> float:
    # Inputs: radius_from is the inner radius in km and radius_to the outer radius of the assessed area
    # Returns the disamenity costs in €/turbine/person/year

    # Distance in km at which disamenity costs become zero
    d0 = 4

    assert (radius_to > 0) & (radius_from >= 0), 'radius must be positive'
    assert radius_to > radius_from, 'radius_to must be larger than radius_from'
    assert radius_to <= d0, f'radius_to exceeds the maximal distance of {d0} km'

    # Cost function
    a = - 3.6
    c = - a * np.log(d0)
    area_weighted_costs = \
        a/2 * (
            radius_to**2 * (2 * np.log(radius_to) - 1)
            - (radius_from**2 * (2 * np.log(radius_from) - 1))
        ) / (
            radius_to**2
            - radius_from**2
        ) + c

    return area_weighted_costs


def calculate_disamenity(distances, source_paths, destination_path):
    # Calculates the disamenity costs in €/turbine/year

    assert len(distances) == len(source_paths), f'distances (len = {len(distances)}) and source_paths {len(source_paths)} have differnet length'
    assert distances == sorted(distances), f'distances should be sorted form smallest to greatest, whereas I got {distances}'

    previous_source_path = None
    previous_distance    = 0.2
    previous_transform   = None
    previous_crs         = None

    cumulated_disamenity = 0

    for distance, source_path in zip(distances, source_paths):

        # Population in a counted between two distances
        population = tif_data(source_path) - (tif_data(previous_source_path) if previous_source_path is not None else 0)
        disamenity = disamenity_costs(radius_from=previous_distance, radius_to=distance)

        # Sums in every iteration the disamenity
        print(f'QA disamenity cost map {disamenity}')
        print(tif_values(full_path=source_path, coordinates=[(4214100, 3539499), (4214700, 3539099)]))
        cumulated_disamenity += population * disamenity

        # QA that affine transform matrices are consistent
        transform = tif_transform(source_path)
        crs       = tif_crs(source_path)

        assert (transform == previous_transform) | (previous_transform is None), 'You are iterating over .tif files that have different affine transform matices'
        assert (crs       == previous_crs      ) | (previous_crs       is None), 'You are iterating over .tif files that have different crs properties'

        # Setting the next iteration
        previous_source_path = source_path
        previous_distance = distance
        previous_transform = transform
        previous_crs = crs

    write_tif(
        full_path=destination_path,
        data=cumulated_disamenity, # type: ignore
        transform=transform, # type: ignore
        crs=crs, # type: ignore
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_paths", type=str, nargs="*")
    parser.add_argument("--distances", type=int, nargs="*")
    parser.add_argument("destination_path", type=str)

    calculate_disamenity(
        **vars(parser.parse_args())
    )
