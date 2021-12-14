import os
import pathlib
import rasterio

import numpy as np

from dataclasses import dataclass
from typing import Protocol

from scipy import signal


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
    force_create: bool = True

    def __post_init__(self):
        exists = os.path.isfile(self.full_path)

        if exists and not self.force_create:
            print(f'{self.tif_generator.file} exists, no need to create a new one')
        else:
            self.tif_generator.create()
            print(f'{self.tif_generator.file} created')

    @property
    def full_path(self):
        return os.path.join(self.tif_generator.folder, self.tif_generator.file)

    @property
    def data(self):
        with rasterio.open(self.full_path) as dataset:
            # Only 1 band supported
            index, = dataset.indexes
            data = dataset.read(index)
        return data

    @property
    def transform(self):
        with rasterio.open(self.full_path) as dataset:
            # Only 1 band supported
            transform = dataset.transform
        return transform


if __name__ == '__main__':
    pass
