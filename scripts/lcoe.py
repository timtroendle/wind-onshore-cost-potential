import argparse

import rioxarray

HOURS_PER_YEAR = 8760


def calculate_lcoe(investment_costs, annual_maintenance_costs, path_to_capacity_factors,
                   discount_rate, lifetime, availability, path_to_output_lcoe, path_to_output_energy):
    assert 0 <= discount_rate <= 1
    assert 0 <= availability <= 1
    capacity_factors = rioxarray.open_rasterio(path_to_capacity_factors)

    annuity_factor = _present_value_of_annuity_factor(discount_rate, lifetime)

    annual_costs = investment_costs * annuity_factor + annual_maintenance_costs
    annual_energy = capacity_factors * HOURS_PER_YEAR * availability
    lcoe = annual_costs / annual_energy
    lcoe.rio.to_raster(path_to_output_lcoe) # TODO compress data
    annual_energy.rio.to_raster(path_to_output_energy)


def _present_value_of_annuity_factor(discount_rate, lifetime):
    nominator = ((1 + discount_rate) ** lifetime) * discount_rate
    denominator = ((1 + discount_rate) ** lifetime) - 1
    if discount_rate == 0:
        return 1 / lifetime
    else:
        return nominator / denominator


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_capacity_factors", type=str)
    parser.add_argument("investment_costs", type=float)
    parser.add_argument("annual_maintenance_costs", type=float)
    parser.add_argument("discount_rate", type=float)
    parser.add_argument("lifetime", type=int)
    parser.add_argument("availability", type=float)
    parser.add_argument("path_to_output_lcoe", type=str)
    parser.add_argument("path_to_output_energy", type=str)

    calculate_lcoe(
        **vars(parser.parse_args())
    )
