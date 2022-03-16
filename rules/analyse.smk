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
    output:
        lcoe = "build/data/lcoe-eur-per-mwh.tif",
        annual_energy = "build/data/annual-energy-mwh.tif"
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


rule population_in_radius:
    message: "Create map of population counts within {wildcards.distance}km."
    input:
        script = "scripts/population.py",
        population = rules.population.output[0]
    output: "build/population-within-{distance}km.tif"
    conda: "../envs/default.yaml"
    shell: "python {input} {wildcards.distance} {output}"


rule disamenity_cost:
    message: "Create map of disamenity cost."
    input:
        script = "scripts/disamenity_cost.py",
        maps = expand("build/population-within-{distance}km.tif", distance=config["parameters"]["distances-in-km"])
    params: distances = config["parameters"]["distances-in-km"]
    output: "build/disamenity-cost.tif",
    conda: "../envs/default.yaml"
    shell: "python {input.script} {output} --source_paths {input.maps} --distances {params.distances}"


rule country_shape:
    message: "Isolate {wildcards.country_id} shape from all NUTS."
    input:
        script = "scripts/country_shape.py",
        shape = rules.nuts.output.shp,
    output: "build/data/shapes/{country_id}.shp"
    conda: "../envs/default.yaml"
    shell: "python {input} {wildcards.country_id} {output}"


rule turbine_placement:
    message: "Determine locations of turbines in {wildcards.country_id}."
    input:
        script = "scripts/turbine_locations.py",
        shape = "build/data/shapes/{country_id}.shp",
        priors = rules.priors.output
    output:
        csv = "build/turbine-locations-{country_id}.csv",
        tif = "build/turbine-locations-{country_id}.tif"
    conda: "../envs/glaes.yaml"
    shell: "python {input} {output}"


rule cost_per_turbine:
    message: "Spatially merge turbines and their costs."
    input:
        script = "scripts/merge.py",
        turbines = rules.turbine_placement.output.csv,
        lcoe = rules.lcoe.output.lcoe,
        annual_energy = rules.lcoe.output.annual_energy,
        disamenity_cost = rules.disamenity_cost.output,
        population = expand("build/population-within-{distance}km.tif", distance=config["parameters"]["distances-in-km"])
    params: distances = config["parameters"]["distances-in-km"]
    output: "build/turbines-{country_id}.csv"
    conda: "../envs/default.yaml"
    shell: "python {input} {output} --distances {params.distances}"


rule cost_potential_curve:
    message: "Plot cost potential curve."
    input:
        script = "scripts/plot.py",
        turbines = rules.cost_per_turbine.output
    output: "build/cost-potential-curve-{country_id}.png"
    conda: "../envs/default.yaml"
    shell: "python {input} {output}"
