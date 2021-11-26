import os
import requests
import rasterio

from typing import Protocol
from zipfile import ZipFile
from dataclasses import dataclass

import math
import numpy as np
import pandas as pd
from affine import Affine
from scipy import signal # TODO: add to envs

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
    # TODO: From JN - Consider cleaning up this chunk of code
    # TODO: QA bug - When radius=1 the center is not the cell with the highest number
    # TODO: Adapt logic such that the 2-D array means actually "within" radius, rather than "between" radius-x and radius+x
    # TODO: Consider using drawing from a Uniform distribution "Monte-Carlo"-like, where the number of samples is a function input
    
    width = 0.5
    resolution = 20
    step = 1/resolution
    
    rng = range(-radius-1,radius+2)
    df = pd.DataFrame(index=rng, columns=rng, dtype=np.float64)

    for x in rng:
        for y in rng:
            count = 0
            for x0 in np.arange(-0.5, 0.5, step):
                for y0 in np.arange(-0.5, 0.5, step):
                    for x1 in np.arange(x-0.5, x+0.5, step):
                        for y1 in np.arange(y-0.5, y+0.5, step):
                            distance = math.sqrt((x1-x0)**2 + (y1-y0)**2)
                            if (radius - width <= distance) & (distance < radius + width):
                                count += 1 / resolution**4
            df.loc[x, y] = float(count)
    
    return df.values


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

        with rasterio.open(self._full_path) as dataset:
            # Only 1 band supported
            index, = dataset.indexes      
            data = dataset.read(index)
        return data
    
    @property
    def transform(self):
        self.create()

        with rasterio.open(self._full_path) as dataset:
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
            full_path=os.path.join(self.file(), self.folder()),
            data = data,
            transform = population.transform
        )


## If you what to import a open tif file to play around
# pop = rasterio.open(os.path.join(DIR_DATA, 'population.tif'))

if __name__ == '__main__':
    from matplotlib import pyplot as plt
    
    
    ## Plot mask
    import seaborn as sns # TODO: if we keep using this, add to envs packages
    mask = within_radius_mask(radius=3)
    sns.heatmap(mask, annot=True)
    plt.show()
    
    ## Plot population
    # population = TifManager(Population())
    # plt.imshow(population.data, cmap=plt.get_cmap('gray_r'), vmin=0, vmax=1000)
    # plt.show()
 
