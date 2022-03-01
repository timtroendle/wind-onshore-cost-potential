from scripts.population import generate_population_in_radius
from scripts.disamenity_cost import calculate_disamenity
from scripts.merge import test_merge


population = r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\population.tif"


population_in_radius =[
    r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\population_1.tif",
    r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\population_2.tif",
    r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\population_4.tif",
]
distances=[1,2,4]

disamenity = r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\disamenity.tif"

# generate_population(
#     destination_path = population,
# )

"""
for destination_path, distance in zip(population_in_radius, distances):
    generate_population_in_radius(
        source_path=population,
        destination_path=destination_path,
        distance=distance,
    )



calculate_disamenity(
    distances=distances,
    source_paths=population_in_radius,
    destination_path=disamenity
)
"""

test_merge(
    path_to_turbine_locations=r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\turbine-locations-LU.csv",
    path_to_annual_energy=r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\data\annual-energy-mwh.tif",
    path_to_disamenity_cost=r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\disamenity-cost.tif",
    path_to_lcoe=r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\data\lcoe-eur-per-mwh.tif",
    path_to_output=r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\turbine-LU TEST.csv",
)
