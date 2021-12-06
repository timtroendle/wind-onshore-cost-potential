"""Rules preprocessing raw data."""


rule capacity_factors:
    message: "Warp capacity factors to destination CRS and resolution."
    input:
        raw = rules.download_capacity_factors.output[0],
        reference = rules.population.output[0]
    output: "build/data/capacity-factors.tif"
    conda: "../envs/default.yaml"
    shell: "rio warp {input.raw} -o {output} --like {input.reference} --resampling average" # TODO check resampling


rule road_proximity:
    message: "Warp road proximity to destination CRS and resolution."
    input:
        raw = rules.download_road_proximity.output[0],
        reference = rules.population.output[0]
    output: "build/data/road-proximity.tif"
    conda: "../envs/default.yaml"
    shell: "rio warp {input.raw} -o {output} --like {input.reference} --resampling min" # TODO check resampling
