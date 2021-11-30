"""Rules to download raw data."""


rule download_population:
    message: "Download population data."
    params: url = config["data-sources"]["population"]
    output: protected("data/automatic/raw-population.zip")
    conda: "../envs/shell.yaml"
    shell: "curl -sLo {output} '{params.url}'"


rule population:
    message: "Unzip population data."
    input:
        rules.download_population.output[0]
    output:
        tif = "build/data/population/JRC_1K_POP_2018.tif",
        doc = "build/data/population/JRC-GEOSTAT_2018_TechnicalFactsheet.pdf"
    conda: "../envs/shell.yaml"
    shadow: "minimal"
    shell: "unzip -o {input} -d build/data/population"


rule download_capacity_factors:
    message: "Download capacity factors."
    params: url = config["data-sources"]["capacity-factors"]
    output: protected("data/automatic/raw-capacity-factors.tif")
    conda: "../envs/shell.yaml"
    shell: "curl -sLo {output} '{params.url}'"
