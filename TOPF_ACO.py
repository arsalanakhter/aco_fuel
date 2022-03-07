# generate graph
# - depots D
# - tasks T
# - rewards R_t

# number of robots N
# number of ant pools A

import numpy as np
import sys

from TOPF_ACO_AntPool import TOPF_ACO_AntPool


class TOPF_ACO:

    def __init__(self, rng, pools, robots, graph, start_node, fuelf, timef,
                 max_fuel, max_time, heuristicf, pheromonef, obj_fn):
        self.rng = rng
        self.pools = [TOPF_ACO_AntPool(i, robots, graph, start_node, fuelf,
                                       timef, max_fuel, max_time, heuristicf,
                                       pheromonef, obj_fn)
                      for i in range(0, pools)]
        self.pheromone_matrix = np.zeros((graph.num_nodes(), graph.num_nodes(),
                                          robots))
        self.pheromone_growth_constant = 100
        self.best_paths_global = []
        self.best_objective_val_global = 0
        self.pool_fuel_best_global = {}

    def decay_pheromone(self):
        pass

    def lay_pheromone(self, pool, graph):
        """Lays the pheromone after each iteration, when the ants come up
        with paths
        """
        for ant in pool.ants:
            path = ant.path
            for i in range(len(path) - 1):
                # Handle the case for division by zero
                delta_pheromone_value = \
                    self.pheromone_growth_constant / (
                            ant.distance_travelled + 0.000001)
                self.pheromone_matrix[path[i], path[i + 1],
                                      ant.id] += delta_pheromone_value
                self.pheromone_matrix[path[i + 1], path[i],
                                      ant.id] += delta_pheromone_value
            # Also, ensure no pheromone get laid on a node, i.e. there are
            # no self loops
            for i in range(graph.num_nodes()):
                self.pheromone_matrix[i, i, ant.id] = 0

    def run(self, max_iterations, plot_update_func, graph):
        """Performs a full run"""
        for t in range(0, max_iterations):
            for pool in self.pools:
                pool.reset()
                best_paths, best_objective_val, pool_fuel = \
                    pool.compute_paths(self.rng, self.pheromone_matrix)
                if best_objective_val >= self.best_objective_val_global:
                    self.best_paths_global = best_paths
                    self.best_objective_val_global = best_objective_val
                    self.pool_fuel_best_global = pool_fuel
            self.decay_pheromone()
            for pool in self.pools:
                self.lay_pheromone(pool, graph)
            print(f'Iter:{t}', self)
            print(f'Best Path(s): {self.best_paths_global}')
            print(f'Best Path(s) Lengths: '
                  f'{self.best_objective_val_global:0.5f}\n\n')
            plot_update_func(self.pheromone_matrix, self.best_paths_global)

        return self.pool_fuel_best_global, \
               self.best_paths_global, \
               self.best_objective_val_global

    def __str__(self):
        s = "TOPF_ACO\n"
        for p in self.pools:
            s += str(p)
        return s
