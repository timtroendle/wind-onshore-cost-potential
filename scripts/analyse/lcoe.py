import rioxarray

HOURS_PER_YEAR = 8760


def calculate_lcoe(investment_costs, annual_maintenance_costs, path_to_capacity_factors,
                   discount_rate, lifetime, availability, path_to_output):
    assert 0 <= discount_rate <= 1
    assert 0 <= availability <= 1
    capacity_factors = rioxarray.open_rasterio(path_to_capacity_factors)

    annuity_factor = _present_value_of_annuity_factor(discount_rate, lifetime)

    annual_costs = investment_costs * annuity_factor + annual_maintenance_costs
    annual_energy = capacity_factors * HOURS_PER_YEAR * availability
    lcoe = annual_costs / annual_energy
    lcoe.rio.to_raster(path_to_output) # TODO compress data


def _present_value_of_annuity_factor(discount_rate, lifetime):
    nominator = ((1 + discount_rate) ** lifetime) * discount_rate
    denominator = ((1 + discount_rate) ** lifetime) - 1
    if discount_rate == 0:
        return 1 / lifetime
    else:
        return nominator / denominator


if __name__ == "__main__":
    calculate_lcoe(
        investment_costs=snakemake.params.investment_cost,
        annual_maintenance_costs=snakemake.params.annual_maintenance_cost,
        path_to_capacity_factors=snakemake.input.capacity_factors,
        discount_rate=snakemake.params.discount_rate,
        lifetime=snakemake.params.lifetime,
        availability=snakemake.params.availability,
        path_to_output=snakemake.output[0]
    )
