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
    '''
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
''';
########################################
