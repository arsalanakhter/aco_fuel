# generate graph
# - depots D
# - tasks T
# - rewards R_t

# number of robots N
# number of ant pools A

import numpy as np
import math
import sys


########################################
# Globals
# MAX_TIME = 5.0

########################################

class Graph:

    def __init__(self, depots, tasks):
        self.nodes = np.random.random((depots + tasks, 2))
        self.depots = depots
        self.tasks = tasks
        self.adj_dist = np.zeros((depots + tasks, depots + tasks))
        for i in range(0, depots + tasks):
            for j in range(i + 1, depots + tasks):
                diffx = self.nodes[i][0] - self.nodes[j][0]
                diffy = self.nodes[i][1] - self.nodes[j][1]
                self.adj_dist[i, j] = math.sqrt(diffx * diffx + diffy * diffy)
                self.adj_dist[j, i] = self.adj_dist[i, j]
        self.adj_time = self.adj_dist.copy()

    def num_nodes(self):
        return self.depots + self.tasks

    def dist(self, i, j):
        return self.adj_dist[i, j]

    def time(self, i, j):
        return self.adj_time[i, j]

    def closest_depot_to(self, node):
        d_loc = sys.float_info.max
        d_idx = -1
        for i in range(0, self.depots):
            if self.adj_dist[i, node] < d_loc:
                d_loc = self.adj_dist[i, node]
                d_idx = i
        return d_idx

    def __str__(self):
        s = "Nodes:\n"
        s += str(self.nodes) + "\nAdjacency:\n"
        s += str(self.adj_dist)
        return s


########################################

class TOPF_ACO_Ant:

    def __init__(self, start_node, fuelf, timef, max_time):
        self.start_node = start_node
        self.fuelf = fuelf
        self.timef = timef
        self.max_time = max_time
        self.reset()

    def reset(self):
        self.current_node = self.start_node
        self.fuel = 1.0  # Assuming max_fuel to be 1.0
        self.time_available = self.max_time
        self.isdone = False
        self.path = [self.current_node]

    def move(self, graph, feasible, rng):
        """
        Picks the next node at random and updates the fuel
        :param graph: The graph
        :param feasible: List of pairs (node idx, prob)
        :param rng: The random number generator
        """
        # Pick next node
        x = rng.random()
        y = 0.0
        pick = -1
        for f in feasible:
            y += f[1]
            if x < y:
                pick = f[0]
                break
        # Update fuel
        self.fuel = self.fuelf(self.fuel, graph, self.current_node, pick)
        # Update time
        self.time_available = self.timef(self.time_available, graph, self.current_node, pick)
        # Update current node
        self.current_node = pick
        self.path.append(pick)
        return pick

    def done(self):
        """
        Sets this ant as done by moving it to a depot.
        """
        self.isdone = True

    def fuel_left(self):
        return self.fuel

    def time_left(self):
        return self.time_available

    def __str__(self):
        return "node: " + str(self.current_node) + ", fuel: " + str(self.fuel)


########################################

class TOPF_ACO_AntPool:
    """An ant pool is a pool of ants which are employed for one run of ACO"""

    def __init__(self, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef):
        self.n = robots
        self.g = graph
        self.ants = [TOPF_ACO_Ant(start_node, fuelf, timef, max_time) for i in range(0, self.n)]
        self.fuelf = fuelf
        self.timef = timef
        self.max_time = max_time
        self.heuristicf = heuristicf
        self.pheromonef = pheromonef
        self.visited_g = [0 for _ in range(self.g.num_nodes())]

    def reset(self):
        for ant in self.ants:
            ant.reset()

    def feasible_for(self, ant):
        """Returns the list of neighbors that the ant can pick"""
        # Feasible if:
        # - Not already visited by any ant in the pool
        # - Can reach node and then depot with fuel left
        # TODO: calculate the heuristic, apply pheromone
        # to return: a list [ (node,prob), (node,prob), ... ]
        feasible_neighbours = [[idx, 1] for idx, i in enumerate(self.visited_g) if i != 1]
        # Remove current node, as we do not want the current node to be a feasible neighbour
        feasible_neighbours.remove([ant.current_node, 1])
        # Based on this ant's fuel, remove those nodes from feasible neighbours which this
        # ant cannot reach
        for n in feasible_neighbours:
            if self.fuelf(ant.fuel_left(), self.g, ant.current_node, n[0]) <= 0:
                n[1] = 0
        feasible_neighbours = [n for n in feasible_neighbours if n[1] > 0]
        # Also remove those neighbours from which the ant cannot reach a depot with
        # fuel_left after visiting current feasible neighbours
        for n in feasible_neighbours:
            fuel_at_n = self.fuelf(ant.fuel_left(), self.g, ant.current_node, n[0])
            for i in range(self.g.depots):
                if self.fuelf(fuel_at_n, self.g, n[0], i) < 0:
                    n[1] = 0
        feasible_neighbours = [n for n in feasible_neighbours if n[1] > 0]

        # Also remove those neighbours from which the ant cannot reach back the start node
        # based on time, after visiting this neighbour. Assuming start node is the
        # first node in the node list
        for n in feasible_neighbours:
            time_at_n = self.timef(ant.time_left(), self.g, ant.current_node, n[0])
            if self.timef(time_at_n, self.g, n[0], ant.start_node) < 0:
                n[1] = 0
        feasible_neighbours = [n for n in feasible_neighbours if n[1] > 0]

        return feasible_neighbours

    def move_ants(self, rng):
        """Picks the next node for each ant"""
        for ant in self.ants:
            f_n = self.feasible_for(ant)
            ant.move(self.g, f_n, rng)

    def find_paths(self, rng):
        # for each ant that is not done
        #   calculate the feasible nodes
        #   if there are feasible nodes, move the ant
        #   if not, move ant deterministically to the closest depot and mark the ants as done
        for ant in self.ants:
            if not ant.isdone:
                fs = self.feasible_for(ant)
                if fs:
                    ant.move(self.g, fs, rng)
                else:
                    ant.done()

    def __str__(self):
        s = "Ant Pool\n"
        for a in self.ants:
            s += "  " + str(a) + "\n"
        return s


########################################

class TOPF_ACO:

    def __init__(self, seed, pools, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef):
        self.rng = np.random.default_rng(seed)
        self.pools = [TOPF_ACO_AntPool(robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef)
                      for i in range(0, pools)]

    def update_pheromone(self, paths):
        pass

    def run(self, max_iterations):
        """Performs a full run"""
        for t in range(0, max_iterations):
            for pool in self.pools:
                paths = pool.find_paths(self.rng)
                self.update_pheromone(paths)
            print(self)

    def __str__(self):
        s = "TOPF_ACO\n"
        for p in self.pools:
            s += str(p) + "\n"
        return s


########################################

class TOPF_ACO_Shared(TOPF_ACO):
    """Pheromone is shared across ants in the pool"""

    def __init__(self, seed, pools, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef):
        super().__init__(seed, pools, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef)
        self.pheromone = np.zeros((graph.num_nodes(), graph.num_nodes()))

    def update_pheromone(self, paths):
        pass


########################################

class TOPF_ACO_NonShared(TOPF_ACO):
    """Pheromone is not shared across ants in the pool"""

    def update_pheromone(self, paths):
        pass


########################################

def fuelf_linear(fuel, graph, cur_node, next_node):
    """Computes the fuel left after visiting next_node from cur_node"""
    return fuel - graph.dist(cur_node, next_node)


########################################

def timef_linear(time, graph, cur_node, next_node):
    """Computes the time left after visiting next_node from cur_node"""
    return time - graph.time(cur_node, next_node)


########################################

def heuristicf_random():
    pass

########################################

def pheromonef(pheromone_matrix, ant_pools):
    """Update the pheromone.
    The Pheromone will be updated in two ways:
    1. Whole pheromone matrix will be decayed based on a coefficient
    2. Ants would add pheromone based on their traversals.
    """
    # 1. Decay according to the formula
    # tau_xy <- (1-rho)*tau_xy	(ACO), where rho is the decay coefficient
    pheromone_decay_coefficient = 0.4
    pheromone_growth_constant = 100
    for x in range(len(pheromone_matrix)):
        for y in range(len(pheromone_matrix)):
            pheromone_matrix[x, y] = (1-pheromone_decay_coefficient)*pheromone_matrix[x, y]

    # 2. Add ant pheromone
    # tau_xy <- tau_xy + delta tau_xy_k
    # where: 	delta tau_xy_k = Q / L_k
    for pool in ant_pools:
        for ant in pool:
            path = ant.path
            for i in range(len(path)-1):
                # find the pheromone over this edge
                current_pheromone_value = pheromone_matrix[path[i]][path[i + 1]])

                # update the pheromone along that section of the route
                # (ACO)
                #	delta tau_xy_k = Q / L_k
                new_pheromone_value = pheromone_growth_constant / ant.get_distance_travelled()

                self.ant_pheromone_temp_matrix[route[i]][route[i + 1]] = current_pheromone_value + new_pheromone_value
                self.ant_pheromone_temp_matrix[route[i + 1]][route[i]] = current_pheromone_value + new_pheromone_value

    pass

########################################

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
