
import os
import rasterio
import rasterio.crs

import numpy as np

from typing import List
from affine import Affine
from zipfile import ZipFile


def unzip_file(file_name, archive, destination_folder) -> str:
    file_full_path = os.path.join(destination_folder, file_name)

    if os.path.isfile(file_full_path):
        return file_full_path

    with ZipFile(archive, 'r') as zipObj:
        listOfiles = zipObj.namelist()
        if file_name not in listOfiles:
            raise Exception(
                f'Error: the file named {file_name} is not contained in the archive {archive}. Use one of the following file names:',
                listOfiles)
        else:
            zipObj.extract(file_name, destination_folder)
            return file_full_path


def tif_data(full_path, replace_nodata=None):
    with rasterio.open(full_path) as dataset:
        # Only 1 band supported
        index, = dataset.indexes
        data = dataset.read(index)
        if replace_nodata is not None:
            data = np.where(data == dataset.nodata, replace_nodata, data)
    return data


def tif_transform(full_path):
    with rasterio.open(full_path) as dataset:
        transform = dataset.transform
    return transform


def tif_crs(full_path):
    with rasterio.open(full_path) as dataset:
        crs = dataset.crs
    return crs


def tif_values(full_path: str, coordinates: List[tuple]) -> List[float]:
    """Returns the values correspoing to the input coordinates"""
    
    # Decompose into x and y coordinates
    xs, ys = np.array(coordinates).transpose() 
    
    with rasterio.open(full_path) as src:
        rows, cols = rasterio.transform.rowcol(src.transform, xs, ys)
        index, = src.indexes
        data = src.read(index)

    return [data[row, col] for row, col in zip(rows, cols)]


def write_tif(full_path: str, data: np.ndarray, transform: Affine, crs: rasterio.crs.CRS):
    # https://rasterio.readthedocs.io/en/latest/quickstart.html#opening-a-dataset-in-writing-mode

    height, width = data.shape
    dtype = data.dtype
    print("Called write_tif with ouput path:", full_path)
    with rasterio.open(
        full_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=dtype,
        crs=crs,
        compress='lzw',  # TODO: Are we sure that the original .tif was losslessly comporessed, and here also?
        transform=transform,
    ) as dst:
        dst.write(data, 1)


if __name__ == '__main__':
    pass
