from Graph import Graph
from TOPF_ACO_Shared import TOPF_ACO_Shared

from utils import fuelf_linear, timef_linear

from numpy.random import default_rng

seed = 12345
rng = default_rng(seed)

g = Graph(rng,   # random number generator
          10,    # No. of depots
          10     # No. of Tasks
          )

aco = TOPF_ACO_Shared(
    rng,    # random number generator
    1,      # pools
    3,      # ants
    g,      # graph
    0,      # start_node
    fuelf_linear,  # fuel function
    timef_linear,  # time function
    100.0,         # max_time
    None,          # heuristic function
    None           # pheromone function
)
aco.run(10          # number of iterations
        )
