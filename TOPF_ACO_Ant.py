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

