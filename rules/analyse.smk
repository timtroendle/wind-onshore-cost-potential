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


rule country_shape:
    message: "Isolate {wildcards.country_id} shape from all NUTS."
    input:
        script = "scripts/country_shape.py",
        shape = rules.nuts.output.shp,
    output: "build/data/shapes/{country_id}.shp"
    conda: "../envs/default.yaml"
    shell: "python {input} {wildcards.country_id} {output}"


rule turbine_placement:
    message: "Determine locations of turbines."
    input:
        script = "scripts/turbine_locations.py",
        shape = "build/data/shapes/{country_id}.shp",
        priors = rules.priors.output
    output:
        csv = "build/turbine-locations-{country_id}.csv",
        tif = "build/turbine-locations-{country_id}.tif"
    conda: "../envs/glaes.yaml"
    shell: "python {input} {output}"
