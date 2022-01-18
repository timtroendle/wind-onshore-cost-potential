"""Rules to download raw data."""
from pathlib import Path
from urllib.parse import urlparse

from snakemake.remote.HTTP import RemoteObject
from snakemake.remote.HTTP import RemoteProvider as BaseRemoteProvider


class HTTPRemoteProvider(BaseRemoteProvider):

    def remote(self, value, *args, insecure=None, **kwargs):
        url = urlparse(value)
        assert url.scheme in ["http", "https"]
        url = "".join(url[1:]) # remove scheme
        return super(BaseRemoteProvider, self).remote(url, *args, **kwargs)


HTTP = HTTPRemoteProvider()


rule download_population:
    message: "Download population data."
    input: HTTP.remote(config["data-sources"]["population"])
    output: protected("data/automatic/raw-population.zip")
    run:
        Path(input[0]).rename(output[0])


rule population:
    message: "Unzip population data."
    input:
        rules.download_population.output[0]
    output:
        tif = "build/data/population/JRC_1K_POP_2018.tif",
        doc = "build/data/population/JRC-GEOSTAT_2018_TechnicalFactsheet.pdf"
    shadow: "minimal"
    run:
        import zipfile
        with zipfile.ZipFile(input[0], 'r') as zip_ref:
            zip_ref.extractall("build/data/population")


rule download_capacity_factors:
    message: "Download capacity factors."
    input: HTTP.remote(config["data-sources"]["capacity-factors"])
    output: protected("data/automatic/raw-capacity-factors.tif")
    run:
        Path(input[0]).rename(output[0])


rule download_nuts:
    message: "Download NUTS shape files."
    input: HTTP.remote(config["data-sources"]["nuts"])
    output: protected("data/automatic/raw-nuts.zip")
    run:
        Path(input[0]).rename(output[0])


rule nuts:
    message: "Unzip NUTS data."
    input:
        rules.download_nuts.output[0]
    output:
        shp = "build/data/NUTS_2013_01M_SH/data/NUTS_RG_01M_2013.shp",
        aux = expand("build/data/NUTS_2013_01M_SH/data/NUTS_RG_01M_2013.{suffix}", suffix=["dbf", "prj", "sbn", "sbx", "shp.xml", "shx"]),
        doc = "build/data/NUTS_2013_01M_SH/readme.txt"
    shadow: "minimal"
    run:
        import zipfile
        with zipfile.ZipFile(input[0], 'r') as zip_ref:
            zip_ref.extractall("build/data/")


rule download_priors:
    message: "Download GLAES priors."
    input: HTTP.remote(config["data-sources"]["priors"])
    output: protected("data/automatic/raw-priors.zip")
    run:
        Path(input[0]).rename(output[0])


rule priors:
    message: "Unzip priors data."
    input:
        rules.download_priors.output[0]
    output: directory("build/data/priors")
    shadow: "minimal"
    run:
        import zipfile
        with zipfile.ZipFile(input[0], 'r') as zip_ref:
            zip_ref.extractall("build/data/priors")
