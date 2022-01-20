import argparse
import os
import math
import pathlib

import numpy as np
import pandas as pd

from scipy import signal
from functools import lru_cache
from dataclasses import dataclass


from file_management import write_tif
from tif_manager import TifManager


DIR_PROJECT = pathlib.Path(__file__).parent.resolve().parent.resolve()
DIR_DATA = os.path.join(DIR_PROJECT, 'data')


def within_radius_mask(radius: float) -> np.ndarray:

    @lru_cache(maxsize=128)
    def within_radius(a, b, draws=1000000):
        '''
        This function returns the probability that the distance between a random point in the raster 0, 0 and a random
        point in the raster a, b is smaller than a given radius r.
        :param r: cutoff radius (in km)
        :param a: distance of the rasters in one direction (in km)
        :param b: distnace of the rasters in the other direction (in km)
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


@dataclass
class Population:
    file: str = 'population.tif'
    folder: str = DIR_DATA

    def create(self):
        raise NotImplementedError('The creation is handles by another script')


class PopulationInRadius:
    def __init__(self, radius:int, file:str = None, folder: str = None) -> None:
        self.radius = radius
        self.file = file
        self.folder = folder

    def create(self, source_path = None):

        if source_path is None:
            population = Population()
        else:
            folder, file = os.path.split(source_path)
            population = Population(file=file, folder=folder)

        population = TifManager(population)
        data = signal.convolve2d(
            population.data,
            within_radius_mask(radius=self.radius),
            boundary='wrap',
            mode='same',
        )

        write_tif(
            full_path=os.path.join(self.folder, self.file),
            data = data,
            transform = population.transform
        )


# For snakemake
def generate_population_in_radius(source_path: str, destination_path: str, distance: int):
    folder, file = os.path.split(destination_path)
    PopulationInRadius(radius=distance, file=file, folder=folder).create(source_path=source_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", type=str)
    parser.add_argument("distance", type=int)
    parser.add_argument("destination_path", type=str)

    generate_population_in_radius(
        **vars(parser.parse_args())
    )

