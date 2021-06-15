class TOPF_ACO_Ant:

    def __init__(self, id, start_node, fuelf, timef, max_fuel, max_time):
        self.id = id
        self.start_node = start_node
        self.fuelf = fuelf
        self.timef = timef
        self.max_time = max_time
        self.max_fuel = max_fuel
        self.alpha = 0.5  # Parameter to weigh the effect of pheromone on choosing next node
        self.beta = 1.2  # Parameter to weigh the effect of distance on choosing next node
        self.reset()

    def reset(self):
        self.current_node = self.start_node
        self.fuel = self.max_fuel
        self.time_available = self.max_time
        self.isdone = False
        self.path = [self.current_node]
        self.isdone = False
        self.distance_travelled = 0

    def move(self, graph, feasible, pheromone_matrix, rng):
        """
        Picks the next node at random and updates the fuel
        :param graph: The graph
        :param feasible: List of pairs (node idx, prob)
        :param rng: The random number generator
        """
        # TODO: Check ant move function for its accuracy
        attractiveness = dict()
        sum_total = 0.0

        for possible_next_node in feasible:
            # Check if the ant really need to go to a depot? If there is a single task node
            # available in the feasible nodes, remove all the depot nodes
            feasible.sort()
            if feasible[-1] > graph.depots:  # If the last element in the sorted list is greater than depots,
                feasible = [i for i in feasible if i > graph.depots]  # it means a feasible task exists.
                # Hence only make the tasks to be feasible for selection now. Do not unnecessarily
                # go to depots.

            pheromone = float(pheromone_matrix[self.current_node, possible_next_node, self.id])
            distance = float(graph.dist(self.current_node, possible_next_node))

            attractiveness[possible_next_node] = pow(pheromone, self.alpha) * pow(1 / distance, self.beta)
            sum_total += attractiveness[possible_next_node]

        if sum_total != 0:
            rnd_num = rng.random()
            cumulative = 0.0
            pick = -1
            for possible_next_node in attractiveness:
                weight = attractiveness[possible_next_node] / sum_total
                if rnd_num <= weight + cumulative:
                    pick = possible_next_node
                    break
                cumulative += weight
        else:
            pick = rng.choice(list(attractiveness.keys()))

        # Update fuel
        self.fuel = self.fuelf(self.fuel, graph, self.current_node, pick)
        # Update time
        self.time_available = self.timef(self.time_available, graph, self.current_node, pick)
        # Add distance travelled
        self.distance_travelled += graph.dist(self.current_node, pick)
        # Update current node
        self.current_node = pick
        self.path.append(pick)
        return pick

    def done(self, graph):
        """
        Sets this ant as done when this ant gets back to the starting location.
        """
        self.path.append(self.start_node)
        self.distance_travelled += graph.dist(self.current_node, self.start_node)
        self.isdone = True

    def fuel_left(self):
        return self.fuel

    def time_left(self):
        return self.time_available

    def get_path(self):
        """Return the path of the ant only if the ant is done. Else return None"""
        if self.isdone:
            return self.path
        return None

    def __str__(self):
        return 'Ant ' + str(self.id) + f': node: {self.current_node:02d}' + f', fuel: {self.fuel:.2f}' + \
               ', path_so_far: ' + str(self.path)
