import numpy as np
from TOPF_ACO import TOPF_ACO


class TOPF_ACO_Shared(TOPF_ACO):
    """Pheromone is shared across ants in the pool"""

    def __init__(self, seed, pools, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef):
        super().__init__(seed, pools, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef)
        self.pheromone = np.zeros((graph.num_nodes(), graph.num_nodes()))

    def update_pheromone(self, paths):
        pass
