"""Rules that analyse the data."""


rule lcoe:
    message: "Calculate LCOE from capacity factors."
    input:
        script = "scripts/analyse/lcoe.py",
        capacity_factors = rules.capacity_factors.output[0],
    params:
        investment_cost = config["parameters"]["investment-cost"],
        annual_maintenance_cost = config["parameters"]["annual-maintenance-cost"],
        discount_rate = config["parameters"]["discount-rate"],
        lifetime = config["parameters"]["lifetime"],
        availability = config["parameters"]["availability"]
    output: "build/data/lcoe-eur-per-mwh.tif"
    conda: "../envs/default.yaml"
    shell: "python {input} {params} {output}"


rule lcoe_cdf:
    message: "Visualise the empiricial CDF of LCOE."
    input:
        script = "scripts/analyse/lcoe_ecdf.py",
        lcoe = rules.lcoe.output[0]
    output: "build/lcoe.png"
    conda: "../envs/default.yaml"
    shell: "python {input} {params} {output}"


rule eligibility:
    message: "Determine land eligibility."
    input:
        script = "scripts/analyse/eligibility.py",
        road_proximity = rules.road_proximity.output[0],
    params:
        min_road_distance_in_m = config["parameters"]["eligibility"]["min-road-distance-in-m"]
    output: "build/data/eligibility.tif"
    conda: "../envs/default.yaml"
    shell: "python {input} {params} {output}"
