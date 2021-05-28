from TOPF_ACO_Ant import TOPF_ACO_Ant
from utils import timef_linear


class TOPF_ACO_AntPool:
    """An ant pool is a pool of ants which are employed for one run of ACO"""

    def __init__(self, id, robots, graph, start_node, fuelf, timef, max_time, heuristicf, pheromonef):
        self.id = id
        self.n = robots
        self.g = graph
        self.ants = [TOPF_ACO_Ant(i, start_node, fuelf, timef, max_time) for i in range(0, self.n)]
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
        # to return: a list [ [node,prob], [node,prob], ... ]
        feasible_neighbours = [[idx, 1] for idx, i in enumerate(self.visited_g) if i != 1]
        # Remove first node, as we do not want the first node to be a feasible neighbour for ant
        # to go directly. If there are no fesible neighbouts, we'll send the ant to
        # the starting location manually.
        feasible_neighbours.remove([0, 1])
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

    # def move_ants(self, rng):
    #    """Picks the next node for each ant"""
    #    for ant in self.ants:
    #        f_n = self.feasible_for(ant)
    #        pick = ant.move(self.g, f_n, rng)
    #        self.visited_g[pick] = 1

    def compute_paths(self, rng):
        # for each ant that is not done
        #   calculate the feasible nodes
        #   if there are feasible nodes, move the ant, and mark that node as visited
        #   if not, move ant deterministically to the starting location, ensuring that
        #   the move is feasible. Then mark the ant done.
        paths = []
        for ant in self.ants:
            if not ant.isdone:
                fs = self.feasible_for(ant)
                if fs:
                    pick = ant.move(self.g, fs, rng)
                    self.visited_g[pick] = 1
                else:
                    # Check if the ant can reach the starting location from here
                    if self.can_reach_final_node(ant):
                        ant.done()
                    else:
                        raise ValueError("Ant cannot reach final node from current location!")
            else:
                paths.append(ant.get_path())
        return paths

    def can_reach_final_node(self, ant):
        """If there are no feasible nodes left, can the ant reach the final node? We assume the
         start node to be the final node for each ant to reach back, and we check based on time
         left,(Do we need to check fuel_compatibility?)"""
        if self.timef(ant.time_left(), self.g, ant.current_node, ant.start_node) > 0:
            return True
        return False

    def __str__(self):
        s = f'Ant Pool {self.id}\n'
        for a in self.ants:
            s += "  " + str(a) + "\n"
        return s
