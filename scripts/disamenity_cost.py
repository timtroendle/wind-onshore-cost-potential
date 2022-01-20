import argparse

import numpy as np

from file_management import write_tif, tif_data, tif_transform, tif_crs


def disamenity_costs(radius_from, radius_to, scenario = 'low') -> float:
    # Calculates the disamenity costs in € per person, per annum, per MW installed wind capacity
    # radius from is the inner radius in km and radius_to the outer radius of the assessed area.

    if scenario == 'low':
        cost_slope = -31
        max_distance = 4
    elif scenario == 'high':
        cost_slope = -64
        max_distance = 8
    else:
        print('Not a valid scenario name')

    assert (radius_to > 0) & (radius_from >= 0), 'radius must be positive'
    assert radius_to > radius_from, 'radius_to must be larger than radius_from'
    assert radius_to <= max_distance, f'radius_to exceeds the maximal distance'


    # costs per household, per year, and per windpark
    area_weighted_costs = \
        cost_slope/2 * (
            radius_to**2 * (2*np.log(radius_to) -1)
            -(radius_from**2 * (2*np.log(radius_from) -1)) # TODO: this log(radus_from) does not allow to calculate the the disamenity for an interval starting at zero
        ) / (
            radius_to**2
            -radius_from**2
        ) - cost_slope * np.log(max_distance)

    # Further assumptions
    GBP_EUR = 0.86
    people_household = 2
    turbines_park = 12.5
    MW_turbine = 2

    return(area_weighted_costs / GBP_EUR / people_household / turbines_park / MW_turbine)


def calculate_disamenity(distances, source_paths, destination_path):

    assert len(distances) == len(source_paths), f'distances (len = {len(distances)}) and source_paths {len(source_paths)} have differnet length'
    assert distances == sorted(distances), f'distances should be sorted form smallest to greatest, whereas I got {distances}'

    previous_source_path = None
    previous_distance    = None
    previous_transform   = None
    previous_crs         = None

    cumulated_disamenity = 0

    for distance, source_path in zip(distances, source_paths):
        # Population in a counted betwenn two distances
        population = tif_data(source_path) - (tif_data(previous_source_path) if previous_source_path is not None else 0)
        disamenity = disamenity_costs(
                radius_from = (previous_distance if previous_distance is not None else 0),
                radius_to   = distance,
            )

        # Sums in every iteration the disamenity
        cumulated_disamenity = population * disamenity

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
        data=cumulated_disamenity,
        transform=transform,
        crs=crs,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_paths", type=str, nargs="*")
    parser.add_argument("--distances", type=int, nargs="*")
    parser.add_argument("destination_path", type=str)

    calculate_disamenity(
        **vars(parser.parse_args())
    )
