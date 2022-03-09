"""Rules preprocessing raw data."""


rule annual_capacity_factors:
    message: "Create map of annual capacity factors."
    input:
        script = "scripts/capacityfactors.py",
        raw = rules.download_capacity_factors.output[0],
    output: "build/data/raw-annual-capacity-factors.tif"
    conda: "../envs/default.yaml"
    shell: "python {input} {output}"


rule capacity_factors:
    message: "Warp capacity factors to destination CRS and resolution."
    input:
        raw = rules.annual_capacity_factors.output[0],
        reference = rules.population.output[0]
    output: "build/data/capacity-factors.tif"
    conda: "../envs/default.yaml"
    shell: "rio warp {input.raw} -o {output} --like {input.reference} "
           "--src-nodata 65535.0 --dst-nodata nan --resampling average" # TODO check resampling
