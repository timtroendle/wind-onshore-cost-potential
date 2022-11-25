# Cost-potential curves of onshore wind energy: <br> the role of disamenity costs

This collection estimates the impact of incorporating disamenity costs of wind onshore in Europe (in addition to technology cost). The code and the deriving analyses have been used for the publication:

> Ruhnau, O., Eicke, A., Sgarlato, R., Tröndle, T., Hirth, L., 2022. Cost-potential curves of onshore wind energy: the role of disamenity costs. Environmental and Resource Economics. DOI: [10.1007/s10640-022-00746-2](https://doi.org/10.1007/s10640-022-00746-2)

The philosophy behind this repository is that no intermediary results are included, but all results are computed from raw data and code.

## Getting ready

You need [conda](https://conda.io/docs/index.html) to run the analysis. Using conda, you can create a conda environment from with the required specifications.:

    > conda env create -f environment.yaml
    > conda activate wind-onshore-cost-potential


## Run the analysis

    (wind-onshore-cost-potential) > snakemake --use-conda -j1 --conda-frontend conda

If this command results in an error (Windows: `OSError: [WinError 1314] A required privilege is not held by the client`), try launching the script with Administrator priviledges.

This will run all analysis steps to reproduce results.

You can also run certain parts only by using other `snakemake` rules; to get a list of all rules run `snakemake --list`.

To generate a PDF of the dependency graph of all steps `build/dag.pdf`, run:

    (wind-onshore-cost-potential) > snakemake --use-conda -j1 -f dag --conda-frontend conda


## Repo structure

* `scripts`: contains the Python source code as scripts
* `rules`: contains Snakemake rule definitions
* `envs`: contains execution environments
* `config`: configurations used in the study
* `data`: place for raw data
* `build`: will contain all results (does not exist initially)

## License

The code in this repo is MIT licensed, see `./LICENSE.md`.
