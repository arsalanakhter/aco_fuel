def fuelf_linear(fuel, graph, cur_node, next_node):
    """Computes the fuel left after visiting next_node from cur_node"""
    return fuel - graph.dist(cur_node, next_node)


########################################

def timef_linear(time, graph, cur_node, next_node):
    """Computes the time left after visiting next_node from cur_node"""
    return time - graph.time(cur_node, next_node)


########################################

def topf_aco_individual(g, ants, set_of_paths, best_objective_val_so_far):
    """Objective function for TOPF ACO Global, which is modelled
    in a similar way as TOPF-Global
    Only returns if it did find a better objective value"""
    # Assume reward for each task to be 1 for now
    gamma = 1e-4
    objective_val_this_run = len(set([i for path in set_of_paths
                                      for i in path
                                      if i >= g.depots]))
    pool_fuel_spent_this_run = {
        ant.id: ant.distance_travelled for ant in ants}
    worst_dist_this_run = max(pool_fuel_spent_this_run.values())
    objective_val_this_run -= gamma * worst_dist_this_run
    if objective_val_this_run >= best_objective_val_so_far:
        best_objective_val_so_far = objective_val_this_run
        best_set_of_paths = set_of_paths[:]
        best_pool_fuel_spent = pool_fuel_spent_this_run
        return best_set_of_paths, \
               best_objective_val_so_far, \
               best_pool_fuel_spent

    return None, None, None


########################################

def heuristicf_random():
    pass


########################################

def pheromonef_lay(pheromone_matrix, ant_pools):
    """Update the pheromone.
    The Pheromone will be updated in two ways:
    # 1. Whole pheromone matrix will be decayed based on a coefficient
    2. Ants would add pheromone based on their traversals.
    """
    # 2. Add ant pheromone
    # tau_xy <- tau_xy + delta tau_xy_k
    # where: 	delta tau_xy_k = Q / L_k
    pheromone_growth_constant = 100

    for pool in ant_pools:
        for ant in pool:
            path = ant.path
            for i in range(len(path) - 1):
                # find the pheromone over this edge
                current_pheromone_value = pheromone_matrix[path[i], path[i + 1]]

                # update the pheromone along that section of the route
                # (ACO)
                # delta tau_xy_k = Q / L_k
                new_pheromone_value = pheromone_growth_constant / \
                                      ant.distance_travelled

                pheromone_matrix[path[i]][
                    path[i + 1]] = current_pheromone_value + new_pheromone_value
                pheromone_matrix[path[i + 1]][
                    path[i]] = current_pheromone_value + new_pheromone_value

    return pheromone_matrix
