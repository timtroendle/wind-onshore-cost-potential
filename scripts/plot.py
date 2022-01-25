import argparse

import pandas as pd
import matplotlib.pyplot as plt


def plot(path_to_turbines: str, path_to_output: str):

    capacity = 2
    turbines = pd.read_csv(path_to_turbines, index_col=0)

    plt.figure()

    cumulative_capacity = [x * capacity / 1000 for x in range(len(turbines))]

    engineering_cost = turbines['lcoe_eur_per_mwh'].sort_values()
    plt.plot(cumulative_capacity, engineering_cost, label='Engineering cost')

    disamenity_cost = (turbines['lcoe_eur_per_mwh'] + turbines['disamenity_cost_eur_per_mwh']).sort_values()
    plt.plot(cumulative_capacity, disamenity_cost, label='Engineering cost\n+disamenity cost')

    plt.xlabel('Cumulative capacity (GW)')
    plt.ylabel('Levelized cost of electricity (EUR/MWh)')
    plt.ylim([0, 200])

    plt.legend()

    plt.savefig(path_to_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_turbines", type=str)
    parser.add_argument("path_to_output", type=str)

    plot(
        **vars(parser.parse_args())
    )
