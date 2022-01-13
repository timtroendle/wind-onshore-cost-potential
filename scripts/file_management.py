import os
import requests
import rasterio

import numpy as np

from affine import Affine
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


def tif_data(full_path):
    with rasterio.open(full_path) as dataset:
        # Only 1 band supported
        index, = dataset.indexes
        data = dataset.read(index)
    return data


def tif_transform(full_path):
    with rasterio.open(full_path) as dataset:
        # Only 1 band supported
        transform = dataset.transform
    return transform


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




