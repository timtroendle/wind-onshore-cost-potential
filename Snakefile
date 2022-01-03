configfile: "config/default.yaml"
include: "./rules/download.smk"
include: "./rules/preprocess.smk"
include: "./rules/analyse.smk"
localrules: all, clean

rule all:
    message: "Run entire analysis."
    input:
        "build/lcoe.png",
        "build/data/eligibility.tif"


rule clean: # removes all generated results
    shell:
        """
        rm -r ./build/*
        echo "Data downloaded to data/ has not been cleaned."
        """


rule test:
    conda: "envs/test.yaml"
    output: "build/test-report.html"
    shell:
        "py.test --html={output} --self-contained-html"
