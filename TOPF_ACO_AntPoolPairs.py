from TOPF_ACO_AntPool import TOPF_ACO_AntPool


class TOPF_ACO_AntPoolPairs(TOPF_ACO_AntPool):
    """
    Ant pool pairs are used to run ACO such that we make a pair of ants
    from each pool, and run them, to find the best combination of
    paths for the whole system
    """

    def __init__(self, id, robots, graph, start_node, fuelf, timef, max_fuel,
                 max_time, heuristicf, pheromonef, obj_fn):
        super().__init__(id, robots, graph, start_node, fuelf, timef, max_fuel,
                         max_time, heuristicf, pheromonef, obj_fn)
        self.number_of_ants_in_pool = 20
        self.n = robots
        self.visited_g = {idx: 0 for idx in range(self.g.depots,
                                                  self.g.num_nodes())}
        self.ant_pools = [TOPF_ACO_AntPool(id, self.number_of_ants_in_pool,
                                           graph, start_node,
                         fuelf, timef, max_fuel, max_time, heuristicf,
                         pheromonef, obj_fn) for _ in range(self.n)]

        ant_lists = []
        self.no_of_ant_pairs_done = 0
        for i in range(len(self.ant_pools)):
            ant_lists.append([ant for ant in self.ant_pools[i].ants])
        self.ant_pairs = []
        for i in range(len(ant_lists[0])):
            single_pair = []
            for j in range(len(ant_lists)):
                single_pair.append(ant_lists[j][i])
            self.ant_pairs.append(single_pair)


    def compute_paths(self, rng, pheromone_matrix):
        # for each pair of ants that is not done, calculate feasible tasks
        # (We'll have to make the assumption that we move the pair sequentially
        # i.e. first ant gets a precedence, and the second ant is unfortunate)
        # if there are feasible tasks, move the ant, and mark that
        # task as visited.
        # if there are no feasible tasks, see if all tasks have been
        # visited.
        #       If all tasks have been visited, move the ant
        # deterministically to the starting location, ensuring that
        # the move is feasible. Mark the ant done.
        #       If all tasks have not been visited, randomly move to
        # a feasible depot
        paths = []
        # Continue computing paths until all ants are done
        while self.no_of_ant_pairs_done != len(self.ant_pairs):
            for ant_pair in self.ant_pairs:
                for ant in ant_pair:
                    if not ant.isdone:
                        f_t = self.tasks_feasible_for(ant)
                        if f_t:
                            pick = ant.move(self.g, f_t, pheromone_matrix, rng)
                            self.visited_g[pick] = 1
                        else:
                            # Check if there is still a task that has not been
                            # visited
                            if not all(task for task in self.visited_g.values()):
                                # Randomly Move to a feasible depot
                                f_d = self.depots_feasible_for(ant)
                                f_d = [rng.choice(f_d)]
                                pick = ant.move(self.g, f_d, pheromone_matrix, rng)
                                # Since the ant has reached a feasible depot, set
                                # the fuel to be max fuel
                                ant.fuel = ant.max_fuel
                                # Check if we are at the start node, and  there is
                                # no other node within feasible fuel range
                                if pick == 0:
                                    # First check if enough mission time is still
                                    # available for a visit to any location
                                    # (TODO: and back?)
                                    for node in range(self.g.depots,
                                                      self.g.num_nodes()):
                                        feasible_task = self.timef(ant.time_left(),
                                                                   self.g,
                                                                   pick,
                                                                   node)
                                        # If even a single task can be reached with
                                        # positive time value, break
                                        if feasible_task >= 0:
                                            break
                                        else:
                                            # It means not enough mission time is
                                            # left
                                            # Mark the ant done
                                            ant.done(self.g)
                                            self.no_of_ants_done += 1
                                            break
                                    for node in range(1, self.g.num_nodes()):
                                        feasible = self.fuelf(ant.fuel_left(),
                                                              self.g,
                                                              pick,
                                                              node)
                                        # If even a single node can be reached with
                                        # positive fuel value, break
                                        if feasible >= 0:
                                            break
                                        else:  # Mark the ant done
                                            if not ant.isdone:
                                                ant.done(self.g)
                                                self.no_of_ants_done += 1

                            else:
                                # Check if the ant can reach the starting
                                # location from here
                                if self.can_reach_final_node(ant):
                                    ant.done(self.g)
                                    self.no_of_ants_done += 1
                                else:
                                    raise ValueError("Ant cannot reach final "
                                                     "node from current "
                                                     "location!")
        # Collect all the paths
        for ant in self.ant_pairs:
            paths.append(ant.get_path())
        # Check if the objective value found is the best objective
        # value.
        best_paths, obj_val, fuel_spent = self.obj_fn(self.g, self.ants, paths,
                                                      self.best_objective_val)
        if best_paths:
            self.best_set_of_paths = best_paths
            self.best_objective_val = obj_val
            self.best_pool_fuel_spent = fuel_spent

        # objective_val_this_run = len(set([i for path in paths
        #                                   for i in path
        #                                   if i >= self.g.depots]))
        # pool_fuel_spent_this_run = {
        #     ant.id: ant.distance_travelled for ant in self.ants}
        # for ant in self.ants:
        #     objective_val_this_run -= self.gamma*ant.distance_travelled
        # if objective_val_this_run >= self.best_objective_val:
        #     self.best_objective_val = objective_val_this_run
        #     self.best_set_of_paths = paths[:]
        #     self.best_pool_fuel_spent = pool_fuel_spent_this_run
        return self.best_set_of_paths, \
               self.best_objective_val, \
               self.best_pool_fuel_spent
