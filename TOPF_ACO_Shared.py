import numpy as np
from TOPF_ACO import TOPF_ACO


class TOPF_ACO_Shared(TOPF_ACO):
    """Pheromone is shared across ants in the pool"""

    def __init__(self, seed, pools, robots, graph, start_node, fuelf, timef, max_fuel, max_time, heuristicf, pheromonef):
        super().__init__(seed, pools, robots, graph, start_node, fuelf, timef, max_fuel, max_time, heuristicf, pheromonef)

    def decay_pheromone(self):
        """
        Given the pheromone matrix, decay pheromone
        """
        # 1. Decay according to the formula
        # tau_xy <- (1-rho)*tau_xy	(ACO), where rho is the decay coefficient
        # Used numpy matrices instead of for loop
        pheromone_decay_coefficient = 0.4
        self.pheromone_matrix = (1 - pheromone_decay_coefficient) * self.pheromone_matrix



