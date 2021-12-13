import os
import pathlib


DIR_PROJECT = pathlib.Path(__file__).parent.resolve().parent.resolve()
DIR_DATA = os.path.join(DIR_PROJECT, 'data')