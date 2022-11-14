"""Produces a figure representing the LCOE's cumulated distribution function"""

import argparse

import matplotlib.pyplot as plt
import seaborn as sns
import rioxarray


def visualise_lcoe_cdf(path_to_lcoe, path_to_plot):
    ds = rioxarray.open_rasterio(path_to_lcoe)
    data = ds.to_series().dropna().rename("lcoe").reset_index()

    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    sns.ecdfplot(
        data=data,
        x="lcoe",
        ax=ax,
        legend=False
    )
    ax.set_xlim(0, 100)
    ax.set_xlabel("LCOE (€/MWh)")
    fig.savefig(path_to_plot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_lcoe", type=str)
    parser.add_argument("path_to_plot", type=str)

    visualise_lcoe_cdf(
        **vars(parser.parse_args())
    )
