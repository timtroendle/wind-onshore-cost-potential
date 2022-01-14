from turtle import distance
from scripts.population import generate_population, generate_population_in_radius
from scripts.disamenity_cost import calculate_disamenity, disamenity_costs



population = r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\population.tif"


population_in_radius =[
    r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\population_1.tif",
    r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\population_2.tif",
    r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\population_3.tif",
]
distances=[1,2,3]

disamenity = r"C:\Users\sgarl\Documents\GitHub\wind-externalities\data\disamenity.tif"


generate_population(
    destination_path = population,
)

generate_population_in_radius(
    source_path=population,
    destination_paths=population_in_radius,
    distances=distances,
)

calculate_disamenity(
    distances=distances,
    source_paths=population_in_radius,
    destination_path=disamenity
)