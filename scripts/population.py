import os
import requests
import rasterio

from typing import Protocol
from zipfile import ZipFile
from dataclasses import dataclass
from functools import lru_cache

import math
import numpy as np
import pandas as pd
from affine import Affine
from scipy import signal

from settings import DIR_DATA


def download_url(url, save_path, chunk_size=128) -> str:

    # If file is already downloaded, return
    if os.path.isfile(save_path):
        return save_path

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        # First save with a temporary name, in case the process get interrupted
        temp_name = save_path + '.tmp'
        with open(temp_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
        os.rename(temp_name, save_path)
        return save_path

    else:
        raise Exception(f'Error: request status code is not ok (200): {r.status_code}')


def unzip_file(file_name, archive, destination_folder) -> str:
    file_full_path = os.path.join(destination_folder, file_name)

    if os.path.isfile(file_full_path):
        return file_full_path

    with ZipFile(archive, 'r') as zipObj:
        listOfiles = zipObj.namelist()
        if file_name not in listOfiles:
            raise Exception(f'Error: the file named {file_name} is not contained in the archive {archive}. Use one of the following file names:', listOfiles)
        else:
            zipObj.extract(file_name, destination_folder)
            return file_full_path


def get_JRC_GRID_2018(file_name) -> str:
    archive = download_url(
        url=r'https://ec.europa.eu/eurostat/cache/GISCO/geodatafiles/JRC_GRID_2018.zip',
        save_path=os.path.join(DIR_DATA, r'JRC_GRID_2018.zip')
    )

    return unzip_file(file_name, archive=archive, destination_folder=DIR_DATA)


def write_tif(full_path: str, data: np.ndarray, transform: Affine):
    # https://rasterio.readthedocs.io/en/latest/quickstart.html#opening-a-dataset-in-writing-mode

    height, width = data.shape
    dtype = data.dtype
    print(full_path)
    with rasterio.open(
        full_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=dtype,
        crs='+proj=latlong',    # TODO: QA, maybe can be taken from the original .tif property
        compress='lzw',         # TODO: Are we sure that the original .tif was losslessly comporessed, and here also?
        transform=transform,
    ) as dst:
        dst.write(data, 1)


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
        for i in range(draws):
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


class TifGenerator(Protocol):
    def file(self) -> str:
        ...
    def folder(self) -> str:
        ...
    def create(self) -> None:
        ...


@dataclass
class TifManager:
    tif_generator: TifGenerator

    @property
    def file(self) -> str:
        return self.tif_generator.file()

    @property
    def folder(self) -> str:
        return self.tif_generator.folder()

    @property
    def full_path(self):
        return os.path.join(self.folder, self.file)

    @property
    def exists(self):
        return os.path.isfile(self.full_path)

    def create(self):
        if self.exists:
            print(f'{self.file} exists, no need to create a new one')
        else:
            self.tif_generator.create()
            print(f'{self.file} created')

    @property
    def data(self):

        self.create()

        with rasterio.open(self.full_path) as dataset:
            # Only 1 band supported
            index, = dataset.indexes
            data = dataset.read(index)
        return data

    @property
    def transform(self):
        self.create()

        with rasterio.open(self.full_path) as dataset:
            # Only 1 band supported
            transform = dataset.transform
        return transform


@dataclass
class Population:
    def file(self):
        return 'population.tif'

    def folder(self):
        return DIR_DATA

    def create(self):
        full_path = os.path.join(self.folder(), self.file())
        source_tif = get_JRC_GRID_2018('JRC_1K_POP_2018.tif')

        with rasterio.open(source_tif) as dataset:
            index, = dataset.indexes
            data = dataset.read(index)
            transform = dataset.transform

        data = np.where(data==dataset.nodata, 0, data)

        write_tif(
            full_path=full_path,
            data=data,
            transform=transform,
        )


@dataclass
class PopulationInRadius:
    radius: int

    def file(self):
        return f'population_{self.radius}r.tif'

    def folder(self):
        return DIR_DATA

    def create(self):
        population = TifManager(Population())
        data = signal.convolve2d(
            population.data,
            within_radius_mask(radius=self.radius),
            boundary='wrap',
            mode='same',
        )

        write_tif(
            full_path=os.path.join(self.folder(), self.file()),
            data = data,
            transform = population.transform
        )


## If you what to import a open tif file to play around
# pop = rasterio.open(os.path.join(DIR_DATA, 'population.tif'))

if __name__ == '__main__':
    # Test
    radius1 = TifManager(PopulationInRadius(radius=1))

    # Cost calculation example
    data = radius1.data*100

    # TODO Missing implementations (discuss with Tim on how to integrate his calculations)
    # 1) Filter Germany
    # 2) Implement class with ad-hoc create function for:
    #       - Calculate disamenity
    #       - Calculate annualized costs (not a tiff since constant)
    #       - Calculate FLH
    #       - Calculate LCOE

    # TODO Plotting (discuss)

    """
    from matplotlib import pyplot as plt

    ## Plot mask
    import seaborn as sns  # TODO: if we delete this, delete from environment.yaml
    mask = within_radius_mask(radius=3)
    sns.heatmap(mask, annot=True)
    plt.show()

    ## Plot population
    # population = TifManager(Population())
    # plt.imshow(population.data, cmap=plt.get_cmap('gray_r'), vmin=0, vmax=1000)
    # plt.show()
    """
