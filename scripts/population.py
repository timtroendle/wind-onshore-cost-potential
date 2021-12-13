
import os
import math
import pathlib
import rasterio

import numpy as np
import pandas as pd

from typing import List
from scipy import signal
from functools import lru_cache
from dataclasses import dataclass


from scripts.file_management import write_tif, unzip_file, download_url
from scripts.tif_manager import TifManager, TifGenerator


DIR_PROJECT = pathlib.Path(__file__).parent.resolve().parent.resolve()
DIR_DATA = os.path.join(DIR_PROJECT, 'data')


def within_radius_mask(radius: int) -> np.ndarray:

    @lru_cache(maxsize=128)
    def within_radius(r, a, b, draws=1000000):
        '''
        This function returns the probability that the distance between a random point in the raster 0, 0 and a random
        point in the raster a, b is smaller than a given radius r.
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
            if distance < r:
                count += 1
        return count/draws

    rng = range(-radius, radius+1)
    df = pd.DataFrame(index=rng, columns=rng, dtype=np.float64)
    for x in rng:
        for y in rng:
            a, b = sorted([abs(x), abs(y)])
            df.loc[x, y] = within_radius(radius, a, b)

    return df.round(2).values


def get_JRC_GRID_2018(file_name) -> str:
    archive = download_url(
        url=r'https://ec.europa.eu/eurostat/cache/GISCO/geodatafiles/JRC_GRID_2018.zip',
        save_path=os.path.join(DIR_DATA, r'JRC_GRID_2018.zip')
    )

    return unzip_file(file_name, archive=archive, destination_folder=DIR_DATA)


@dataclass
class Population:
    file: str = 'population.tif'
    folder: str = DIR_DATA

    def create(self):
        source_tif = get_JRC_GRID_2018('JRC_1K_POP_2018.tif')

        with rasterio.open(source_tif) as dataset:
            index, = dataset.indexes
            data = dataset.read(index)
            transform = dataset.transform

        data = np.where(data==dataset.nodata, 0, data)

        write_tif(
            full_path=os.path.join(self.folder, self.file),
            data=data,
            transform=transform,
        )


class PopulationInRadius:
    def __init__(self, radius:int, file:str = None, folder: str = None) -> None:
        self.radius = radius
        self.file   = file   if file   is not None else f'population_{radius}r.tif'
        self.folder = folder if folder is not None else DIR_DATA

    def create(self):
        population = TifManager(Population())
        data = signal.convolve2d(
            population.get_data,
            within_radius_mask(radius=self.radius),
            boundary='wrap',
            mode='same',
        )

        write_tif(
            full_path=os.path.join(self.folder(), self.file()),
            data = data,
            transform = population.get_transform
        )


# For snakemake
def generate_population(destination_path: str):

    folder, file = os.path.split(destination_path)
    _ = TifManager(
        tif_generator=Population(file=file, folder=folder),
        force_create=False, # No neet to rerun the download routine, even if the script changes
    )


# For snakemake
def generate_population_in_radius(source_path: str, destination_paths: List[str], distances: List[int]):
    for distance, destination_path in zip(distances, destination_paths):
        folder, file = os.path.split(destination_path)

        _ = TifManager(tif_generator=PopulationInRadius(radius=distance, file=file, folder=folder))


if __name__ == '__main__':
    generate_population(
        # source_path = snakemake.input.population, # This is downloaded form the data source
        destination_path = snakemake.output.population
    )

    generate_population_in_radius(
        source_path = snakemake.input.population,
        destination_paths = snakemake.output.population_in_radius,
        distances = snakemake.params.distances,
    )

