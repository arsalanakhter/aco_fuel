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
        self.pheromone_matrix = np.zeros((graph.num_nodes(), graph.num_nodes()))
        self.pheromone_growth_constant = 100

    def decay_pheromone(self):
        pass

    def lay_pheromone(self, pool):
        """Lays the pheromone after each iteration, when the ants come up with paths
        """
        for ant in pool.ants:
            path = ant.path
            for i in range(len(path) - 1):
                # find the pheromone over this edge
                current_pheromone_value = self.pheromone_matrix[path[i], path[i + 1]]

                # update the pheromone along that section of the route
                # (ACO)
                # delta tau_xy_k = Q / L_k
                new_pheromone_value = self.pheromone_growth_constant / ant.distance_travelled

                self.pheromone_matrix[path[i]][path[i + 1]] = current_pheromone_value + new_pheromone_value
                self.pheromone_matrix[path[i + 1]][path[i]] = current_pheromone_value + new_pheromone_value

    def run(self, max_iterations):
        """Performs a full run"""
        for t in range(0, max_iterations):
            for pool in self.pools:
                pool.compute_paths(self.rng)
                self.decay_pheromone()
                self.lay_pheromone(pool)
            print(f'Iter:{t}', self)

    def __str__(self):
        s = "TOPF_ACO\n"
        for p in self.pools:
            s += str(p) + "\n"
        return s
