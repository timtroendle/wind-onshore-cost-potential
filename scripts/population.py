import os
import requests
import rasterio

import numpy as np
import pandas as pd

from settings import DIR_DATA
from simpledbf import Dbf5
from zipfile import ZipFile


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



def population_in_radius(radius=None) -> str:

    assert isinstance(radius, int) or radius is None, 'Radius can also be an int or None because of how the file names are generated'

    if radius:
        return NotImplementedError

    file_name = f'poulation_{radius}r.tif' if radius else 'poulation.tif'
    
    file_full_path = os.path.join(DIR_DATA, file_name)
    if os.path.isfile(file_full_path):
        return file_full_path

    source_tif = get_JRC_GRID_2018('JRC_1K_POP_2018.tif')
    dataset = rasterio.open(source_tif)
    
    index, = dataset.indexes
    
    data = dataset.read(index)
    data = np.where(data==dataset.nodata, np.nan, data)

    # https://rasterio.readthedocs.io/en/latest/quickstart.html#opening-a-dataset-in-writing-mode
    with rasterio.open(
        file_full_path,
        'w',
        driver='GTiff',
        height=dataset.height,
        width=dataset.width,
        count=1,
        dtype=data.dtype,
        crs='+proj=latlong',    # TODO: QA, maybe can be taken from the original .tif property
        compress='lzw',         # TODO: Are we sure that the original .tif was losslessly comporessed, and here also?
        transform=dataset.transform,
    ) as dst:
        dst.nodata = 0.0
        dst.write(data, 1)
    
    return file_full_path


if __name__ == '__main__':
    from matplotlib import pyplot
     
    population_tif = population_in_radius()
    
    # src = rasterio.open(population_tif)
    # pyplot.imshow(src.read(1), cmap=pyplot.get_cmap('gray_r'), vmin=0, vmax=1000)
    # pyplot.show()