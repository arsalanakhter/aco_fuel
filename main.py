from Graph import Graph
from TOPF_ACO_Shared import TOPF_ACO_Shared

from utils import fuelf_linear, timef_linear

g = Graph(2, 3)
# print(g)

aco = TOPF_ACO_Shared(
    12345,  # seed
    2,  # pools
    3,  # robots
    g,  # graph
    0,  # start_node
    fuelf_linear,  # fuel function
    timef_linear,  # time function
    5.0,           # max_time
    None,          # heuristic function
    None           # pheromone function
)
aco.run(2)
