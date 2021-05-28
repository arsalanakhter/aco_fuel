# generate graph
# - depots D
# - tasks T
# - rewards R_t

# number of robots N
# number of ant pools A

import numpy as np

from TOPF_ACO_AntPool import TOPF_ACO_AntPool


class TOPF_ACO:

    def __init__(self, rng, pools, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef):
        self.rng = rng
        self.pools = [TOPF_ACO_AntPool(i, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef)
                      for i in range(0, pools)]

    def update_pheromone(self, paths):
        pass

    def run(self, max_iterations):
        """Performs a full run"""
        for t in range(0, max_iterations):
            for pool in self.pools:
                paths = pool.compute_paths(self.rng)
                self.update_pheromone(paths)
            print(f'Iter:{t}', self)

    def __str__(self):
        s = "TOPF_ACO\n"
        for p in self.pools:
            s += str(p) + "\n"
        return s
