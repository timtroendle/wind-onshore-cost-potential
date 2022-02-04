import argparse

import math
import numpy as np
import pandas as pd

from scipy import signal
from functools import lru_cache

from file_management import write_tif, tif_crs, tif_data, tif_transform


def within_radius_mask(radius: float) -> np.ndarray:

    @lru_cache(maxsize=128)
    def within_radius(a, b, draws=1000000):
        '''
        This function returns the probability that the distance between a random point in the raster 0, 0 and a random
        point in the raster a, b is smaller than a given radius r.
        The units of a, b, and r are the resolution of the population raster (currently 1 km)
        :param r: cutoff radius
        :param a: distance of the rasters in one direction
        :param b: distnace of the rasters in the other direction
        :return: probability
        '''
        count = 0
        for _ in range(draws):
            x0, y0 = -0.5 + np.random.random(), -0.5 + np.random.random()
            x1, y1 = a - 0.5 + np.random.random(), b - 0.5 + np.random.random()
            distance = math.sqrt((x1-x0)**2 + (y1-y0)**2)
            if distance < radius:
                count += 1
        return count/draws

    ceil = int(np.ceil(radius))
    rng = range(-ceil, ceil+1)
    df = pd.DataFrame(index=rng, columns=rng, dtype=np.float64)
    for x in rng:
        for y in rng:
            a, b = sorted([abs(x), abs(y)])
            df.loc[x, y] = within_radius(a, b)

    return df.round(2).values


def generate_population_in_radius(source_path: str, destination_path: str, distance: int):

    data = signal.convolve2d(
        tif_data(source_path, replace_nodata=0),
        within_radius_mask(radius=distance),
        boundary='wrap',
        mode='same',
    )


    write_tif(
        full_path=destination_path,
        data = data,
        transform = tif_transform(source_path),
        crs = tif_crs(source_path),
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", type=str)
    parser.add_argument("distance", type=int)
    parser.add_argument("destination_path", type=str)

    generate_population_in_radius(
        **vars(parser.parse_args())
    )

