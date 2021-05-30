import numpy as np
import math
import sys


class Graph:

    def __init__(self, rng, depots, tasks):
        self.rng = rng
        self.nodes = rng.random((depots + tasks, 2))
        self.depots = depots
        self.tasks = tasks
        self.adj_dist = np.zeros((depots + tasks, depots + tasks))
        for i in range(0, depots + tasks):
            for j in range(i + 1, depots + tasks):
                diffx = self.nodes[i][0] - self.nodes[j][0]
                diffy = self.nodes[i][1] - self.nodes[j][1]
                self.adj_dist[i, j] = math.sqrt(diffx * diffx + diffy * diffy)
                self.adj_dist[j, i] = self.adj_dist[i, j]
        self.adj_time = self.adj_dist.copy()   ## TODO: Check deepcopy

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
