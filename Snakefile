configfile: "config/default.yaml"
include: "./rules/download.smk"
include: "./rules/preprocess.smk"
include: "./rules/analyse.smk"
localrules: all, clean

rule all:
    message: "Run entire analysis."
    input:
        "build/cost-potential-curve-DE.png"


rule clean:
    message: "Remove all build results but keep downloaded data."
    run:
        import shutil

        shutil.rmtree("build")
        print("Data downloaded to data/ has not been cleaned.")


rule dag:
    message: "Plotting dependency graph of the workflow."
    output:
        dot = "build/dag.dot",
        pdf = "build/dag.pdf"
    conda: "envs/dag.yaml"
    shell:
        "snakemake --rulegraph > {output.dot} && dot -Tpdf -o {output.pdf} {output.dot}"


rule test:
    conda: "envs/test.yaml"
    output: "build/test-report.html"
    shell:
        "py.test --html={output} --self-contained-html"
