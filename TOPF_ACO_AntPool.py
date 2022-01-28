from TOPF_ACO_Ant import TOPF_ACO_Ant
from utils import timef_linear

import sys


class TOPF_ACO_AntPool:
    """
    An ant pool is a pool of ants which are employed for one run
    of ACO
    """

    def __init__(self, id, robots, graph, start_node, fuelf, timef,
                 max_fuel, max_time, heuristicf, pheromonef):
        self.id = id
        self.n = robots
        self.g = graph
        self.ants = [TOPF_ACO_Ant(
            i, start_node, fuelf, timef, max_fuel,
            max_time) for i in range(0, self.n)]
        self.fuelf = fuelf
        self.timef = timef
        self.max_time = max_time
        self.heuristicf = heuristicf
        self.pheromonef = pheromonef
        self.visited_g = {idx: 0 for idx in range(self.g.depots,
                                                  self.g.num_nodes())}
        self.best_set_of_paths = []
        self.total_distance_of_best_set_of_paths = sys.maxsize
        self.best_pool_fuel_spent = {}

    def reset(self):
        self.visited_g = {idx: 0 for idx in range(self.g.depots,
                                                  self.g.num_nodes())}
        for ant in self.ants:
            ant.reset()

    def tasks_feasible_for(self, ant):
        """Returns the list of tasks that the ant can pick"""
        # Feasible if: - Not already visited by any ant in the pool
        feasible_tasks = [idx for idx, i in self.visited_g.items()
                          if i != 1]
        # Based on this ant's fuel, remove those tasks from feasible
        # neighbours which this ant cannot reach
        to_be_removed = []
        for n in feasible_tasks:
            if self.fuelf(ant.fuel_left(), self.g, ant.current_node, n) <= 0:
                to_be_removed.append(n)
        # Also remove those tasks from which the ant cannot
        # reach a depot with fuel_left after visiting current
        # feasible tasks
        for n in feasible_tasks:
            fuel_at_n = self.fuelf(ant.fuel_left(), self.g, ant.current_node, n)
            for i in range(self.g.depots):
                if self.fuelf(fuel_at_n, self.g, n, i) < 0:
                    to_be_removed.append(n)

        # Also remove those tasks from which the ant cannot
        # reach back the start node based on time, after visiting
        # this task. Assuming start node is the first node in
        # the node list
        for n in feasible_tasks:
            time_at_n = self.timef(ant.time_left(), self.g, ant.current_node, n)
            if self.timef(time_at_n, self.g, n, ant.start_node) < 0:
                to_be_removed.append(n)
        feasible_tasks = [n for n in feasible_tasks if n not in to_be_removed]

        return feasible_tasks

    def depots_feasible_for(self, ant):
        """Returns the list of depots that the ant can pick"""
        # Feasible if:
        # 1) We can go from this depot to the start node
        # 2) There is enough mission time left
        feasible_depots = [i for i in range(self.g.depots)]
        # Based on this ant's fuel, remove those depots from feasible
        # depots which this ant cannot reach
        to_be_removed = []
        for n in feasible_depots:
            if self.fuelf(ant.fuel_left(), self.g, ant.current_node, n) <= 0:
                to_be_removed.append(n)
        # Also remove those depots from which the ant cannot
        # reach a depot with fuel_left after visiting current
        # feasible depots
        for n in feasible_depots:
            fuel_at_n = self.fuelf(ant.fuel_left(), self.g, ant.current_node, n)
            for i in range(self.g.depots):
                if self.fuelf(fuel_at_n, self.g, n, i) < 0:
                    to_be_removed.append(n)

        # Also remove those depots from which the ant cannot
        # reach back the start node based on time, after visiting
        # this depot. Assuming start node is the first node in
        # the node list
        for n in feasible_depots:
            time_at_n = self.timef(ant.time_left(), self.g, ant.current_node, n)
            if self.timef(time_at_n, self.g, n, ant.start_node) < 0:
                to_be_removed.append(n)

        feasible_depots = [n for n in feasible_depots if n not in to_be_removed]

        return feasible_depots

    def compute_paths(self, rng, pheromone_matrix):
        # for each ant that is not done calculate the feasible tasks
        # if there are feasible tasks, move the ant, and mark that
        # tasks as visited.
        # if there are no feasible tasks, see if all tasks have been
        # visited.
        #       If all tasks have been visited, move the ant
        # deterministically to the starting location, ensuring that
        # the move is feasible. Mark the ant done.
        #       If all tasks have not been visited, randomly move to
        # a feasible depot
        paths = []
        no_of_ants_done = 0
        # Continue computing paths until all ants are done
        while no_of_ants_done != len(self.ants):
            for ant in self.ants:
                if not ant.isdone:
                    f_t = self.tasks_feasible_for(ant)
                    if f_t:
                        pick = ant.move(self.g, f_t, pheromone_matrix, rng)
                        self.visited_g[pick] = 1
                    else:
                        # Check if there is still a task that has not been
                        # visited
                        if not any(task for task in self.visited_g.values()):
                            # Move to a feasible depot
                            f_d = self.depots_feasible_for(ant)
                            pick = ant.move(self.g, f_d, pheromone_matrix, rng)
                        else:
                            # Check if the ant can reach the starting
                            # location from here
                            if self.can_reach_final_node(ant):
                                ant.done(self.g)
                                no_of_ants_done += 1
                            else:
                                raise ValueError("Ant cannot reach final "
                                                 "node from current "
                                                 "location!")
        # Collect all the paths
        for ant in self.ants:
            paths.append(ant.get_path())
        # Check if the global set of paths found is better than the
        # current set for this pool
        total_dist_this_run = 0
        pool_fuel_spent_this_run = {
            ant.id: ant.distance_travelled for ant in self.ants}
        for ant in self.ants:
            total_dist_this_run += ant.distance_travelled
        if total_dist_this_run < \
                self.total_distance_of_best_set_of_paths:
            self.total_distance_of_best_set_of_paths = \
                total_dist_this_run
            self.best_set_of_paths = paths[:]
            self.best_pool_fuel_spent = pool_fuel_spent_this_run
        return self.best_set_of_paths, \
               self.total_distance_of_best_set_of_paths, \
               self.best_pool_fuel_spent

    def can_reach_final_node(self, ant):
        """
        If there are no feasible nodes left, can the ant reach the
        final node? We assume the start node to be the final node for
        each ant to reach back, and we check based on time left,
        (Do we need to check fuel_compatibility?)

         :param ant: Ant object
         """
        if self.timef(ant.time_left(),
                      self.g, ant.current_node, ant.start_node) > 0:
            return True
        return False

    def __str__(self):
        s = f'Ant Pool {self.id}\n'
        for a in self.ants:
            s += "  " + str(a) + "\n"
        return s
