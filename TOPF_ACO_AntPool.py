from TOPF_ACO_Ant import TOPF_ACO_Ant


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
