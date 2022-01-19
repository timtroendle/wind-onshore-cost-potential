import argparse

import numpy as np

from .file_management import write_tif, tif_data, tif_transform


def disamenity_costs(radius_from, radius_to, scenario = 'low') -> float:
     # calculates the disamenity costs in € per person, per annum, per MW installed wind capacity
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
    area_weighted_costs = cost_slope/2 *(radius_to**2 * (2*np.log(radius_to) -1) - (radius_from**2 * (2*np.log(radius_from) -1))) / (radius_to**2 - radius_from**2) -  cost_slope * np.log(max_distance);

    # Further assumptions
    GBP_EUR = 0.86
    people_household = 2
    turbines_park = 12.5
    MW_turbine = 2

    return(area_weighted_costs / GBP_EUR / people_household / turbines_park / MW_turbine)


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_paths", type=str, nargs="*")
    parser.add_argument("--distances", type=int, nargs="*")
    parser.add_argument("destination_path", type=str)

    calculate_disamenity(
        **vars(parser.parse_args())
    )
