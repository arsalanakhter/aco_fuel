import networkx as nx


def fuelf_linear(fuel, graph, cur_node, next_node):
    """Computes the fuel left after visiting next_node from cur_node"""
    return fuel - graph.dist(cur_node, next_node)


########################################

def timef_linear(time, graph, cur_node, next_node):
    """Computes the time left after visiting next_node from cur_node"""
    return time - graph.time(cur_node, next_node)


########################################

def topf_aco_individual_min_worst(g, ants, set_of_paths,
                                  best_objective_val_so_far):
    """Objective function for TOPF ACO Individual, which is modelled
    in a similar way as TOPF-Individual. Only the worst distance is minimized.
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

def topf_aco_individual_min_all(g, ants, set_of_paths,
                                best_objective_val_so_far):
    """Objective function for TOPF ACO Individual minimize all routes.
    Only returns if it did find a better objective value"""
    # Assume reward for each task to be 1 for now
    gamma = 1e-4
    objective_val_this_run = len(set([i for path in set_of_paths
                                      for i in path
                                      if i >= g.depots]))
    pool_fuel_spent_this_run = {
        ant.id: ant.distance_travelled for ant in ants}
    for ant in ants:
        objective_val_this_run -= gamma * ant.distance_travelled
        if objective_val_this_run >= best_objective_val_so_far:
            best_objective_val_so_far = objective_val_this_run
            best_set_of_paths = set_of_paths[:]
            best_pool_fuel_spent = pool_fuel_spent_this_run
            return best_set_of_paths, \
                   best_objective_val_so_far, \
                   best_pool_fuel_spent

    return None, None, None


########################################

def heuristicf_edge_length_inverse(distance):
    dist_epsilon = 1e-6  # To handle division by zero
    return 1 / (distance + dist_epsilon)


########################################

def heuristicf_node_degree_sum(graph, node):
    G = nx.from_numpy_matrix(graph)
    return G.degree[node]


########################################

def heuristicf_max_degree_of_node_neighbours(graph, node):
    G = nx.from_numpy_matrix(graph)
    neighbours_iter = G.neighbors(node)
    # Compute maximum degree for any neighbor
    max_deg = 0
    for n in neighbours_iter:
        deg = G.degree[n]
        if deg > max_deg:
            max_deg = deg
    return max_deg


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
