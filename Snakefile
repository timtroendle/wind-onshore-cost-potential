configfile: "config/default.yaml"
include: "./rules/download.smk"
include: "./rules/preprocess.smk"
include: "./rules/analyse.smk"
localrules: all, clean

rule all:
    message: "Run entire analysis."
    input:
<<<<<<< HEAD
        "build/cost-potential-curve-AT.png",
        "build/cost-potential-curve-BE.png",
        "build/cost-potential-curve-BG.png",
        #"build/cost-potential-curve-CH.png",  # not in EU scenario
        #"build/cost-potential-curve-CY.png",  # turbine placement does not work
        "build/cost-potential-curve-CZ.png",
        "build/cost-potential-curve-DE.png",
        "build/cost-potential-curve-DK.png",
        "build/cost-potential-curve-EE.png",
        "build/cost-potential-curve-EL.png",
        "build/cost-potential-curve-ES.png",
        "build/cost-potential-curve-FI.png",
        "build/cost-potential-curve-FR.png",
        "build/cost-potential-curve-HR.png",
        "build/cost-potential-curve-HU.png",
        "build/cost-potential-curve-IE.png",
        "build/cost-potential-curve-IT.png",
        "build/cost-potential-curve-LT.png",
        "build/cost-potential-curve-LU.png",
        "build/cost-potential-curve-LV.png",
        #"build/cost-potential-curve-MT.png",  # turbine placement does not work
        "build/cost-potential-curve-NL.png",
        #"build/cost-potential-curve-NO.png",  # not in EU scenario
        "build/cost-potential-curve-PL.png",
        "build/cost-potential-curve-PT.png",
        "build/cost-potential-curve-RO.png",
        "build/cost-potential-curve-SE.png",
        "build/cost-potential-curve-SI.png",
        "build/cost-potential-curve-SK.png"
=======
        "build/cost-potential-curve-DE.png"
>>>>>>> 4d2718b9ecf52aed183ae2dd36df44acd6569992


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
