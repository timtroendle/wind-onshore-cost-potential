import os
import requests
from zipfile import ZipFile

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


def unzip_file(file_name, archive, destination) -> str:
    if os.path.join(destination, file_name):
        return os.path.join(destination, file_name)

    with ZipFile(archive, 'r') as zipObj:
        listOfiles = zipObj.namelist()
        if file_name not in listOfiles:
            raise Exception(f'Error: the file named {file_name} is not contained in the archive {archive}. Use one of the following file names:', listOfiles)
        else:
            zipObj.extract(file_name, destination)
            return os.path.join(destination, file_name)


def get_file(file_name) -> str:
    archive = download_url(
        url=r'https://ec.europa.eu/eurostat/cache/GISCO/geodatafiles/JRC_GRID_2018.zip',
        save_path=os.path.join(DIR_DATA, r'JRC_GRID_2018.zip')
    )

    return unzip_file(file_name, archive=archive, destination=DIR_DATA)


if __name__ == '__main__':
    get_file('JRC_POPULATION_2018.dbf')