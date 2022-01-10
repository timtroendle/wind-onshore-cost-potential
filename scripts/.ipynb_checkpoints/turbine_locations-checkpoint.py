from dataclasses import dataclass
from typing import List
import numpy as np
from requests.api import get
from scripts.file_management import write_tif
from scripts.tif_manager import TifGenerator, TifManager
from dataclasses import dataclass
import os

from affine import Affine

def get_allowed_locations() -> np.ndarray:
    '''Get list of coordiantes that represend potential locations'''
    return NotImplemented


def count_locations(locations: np.ndarray, transform: Affine) -> np.ndarray:
    '''Return number of locations'''
    return NotImplemented
    


@dataclass
class NumberOfTurbines:
    file: str
    folder: str

    def create(self):
        locations = get_allowed_locations()
        # TODO: implement standard transform here
        
        data = count_locations(
            locations=locations,
            transform=transform,
        )

        write_tif(
            full_path=os.path.join(self.folder, self.file),
            data=data,
            transform=transform,
            )



if __name__=='__main__':
    pass

