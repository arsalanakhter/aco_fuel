from gurobipy import *
import copy
import warnings
import networkx as nx
import csv
import regex as re
import sys

from concorde.tsp import TSPSolver


class TOPF_OptimalF7:

    def __init__(self, g, n_ants, max_ant_fuel, max_mission_time, seed):
        self.iteration = 0  # To be used later for multiple runs
        self.noOfRobots = n_ants
        self.noOfTasks = g.tasks
        self.noOfDepots = g.depots
        self.L = max_ant_fuel
        self.delta = max_ant_fuel
        self.T_max = max_mission_time
        self.vel = 1
        self.thisSeed = seed
        self.K = [f'R{i}' for i in range(n_ants)]
        self.T = [f'T{i}' for i in range(g.tasks)]
        self.D = [f'D{i}' for i in range(g.depots)]
        self.S = ['S0']
        self.E = ['E0']
        self.N = self.D + self.T + self.S + self.E  # This sequence (D,T,S,E) is important for this code to work
        self.T_loc = {self.T[i]: g.nodes[g.depots + i] for i in range(g.tasks)}
        self.D_loc = {self.D[i]: g.nodes[i] for i in range(g.depots)}
        self.S_loc = {self.S[0]: self.D_loc['D0']}
        self.E_loc = {self.E[0]: self.D_loc['D0']}
        self.N_loc = {**self.D_loc, **self.T_loc, **self.S_loc, **self.E_loc}
        self.N_g_mapping = {i: j for i, j in zip(self.N, list(range(g.depots + g.tasks))+[0, 0])}
        # We assume that start and end locations are always depot 0 in this code implementation here
        self.c = {(i1, j1): g.dist(i2, j2) for i1, i2 in zip(self.N, list(range(g.depots + g.tasks))+[0, 0])
                                            for j1, j2 in zip(self.N, list(range(g.depots + g.tasks))+[0, 0]) if i1 != j1}
        self.f = copy.deepcopy(self.c)
        self.arcs = [(i, j, k) for i in self.N for j in self.N if i != j for k in self.K]
        self.arc_ub = [len(self.N) if i[0] == 'D' or j[0] == 'D' else 1 for i, j, _ in self.arcs]
        self.k_y = [(i, k) for i in self.T for k in self.K]
        self.init_model()
        self.sol = {}

    def init_model(self):
        # Initialize the model
        self.model = Model(
            'F7TOBasic-' + '-Seed:' + str(self.thisSeed))
        # Decision variables and their bounds
        x = self.model.addVars(self.arcs, lb=0, ub=self.arc_ub, name="x", vtype=GRB.INTEGER)
        y = self.model.addVars(self.k_y, name="y", vtype=GRB.BINARY)
        r = self.model.addVars(self.N, lb=0, ub=self.L, vtype=GRB.CONTINUOUS, name="r")
        q = self.model.addVars(self.arcs, vtype=GRB.CONTINUOUS, name="q")
        z = self.model.addVar(name="z", vtype=GRB.CONTINUOUS)

        # Objective function
        gamma = 1e-4
        objExpr1 = quicksum(y[i, k] for i in self.T for k in self.K)
        objExpr2 = gamma * z
        objFun = objExpr1 - objExpr2
        self.model.setObjective(objFun, GRB.MAXIMIZE)

        # Constraints
        # For detail on what the constraints signify please see the
        # corresponding section in the report
        c1 = self.model.addConstrs(
            ((quicksum(self.c[i, j] * x[i, j, k] for i in self.N for j in self.N if i != j)) <= z for k in self.K),
            name="c1")

        # c2_1 = self.model.addConstr((quicksum(x[s,j,k] for j in self.N for k in self.K for s in self.S if j not in self.S) == self.noOfRobots), name="c2_1")
        # c2_2 = self.model.addConstr((quicksum(x[i,e,k] for i in self.N for k in self.K for e in self.E if i!=e) == self.noOfRobots), name="c2_2")

        c3_1 = self.model.addConstrs(
            ((quicksum(x[s, j, k] for s in self.S for j in self.N if j not in self.S)) == 1 for k in self.K),
            name="c3_1")
        c4_1 = self.model.addConstrs(
            ((quicksum(x[j, s, k] for s in self.S for j in self.N if j not in self.S)) == 0 for k in self.K),
            name="c3_2")
        c3_2 = self.model.addConstrs(
            ((quicksum(x[i, e, k] for e in self.E for i in self.N if i not in self.E)) == 1 for k in self.K),
            name="c4_1")
        c4_2 = self.model.addConstrs(
            ((quicksum(x[e, i, k] for e in self.E for i in self.N if i not in self.E)) == 0 for k in self.K),
            name="c4_2")

        c5_1 = self.model.addConstrs(((quicksum(x[i, h, k] for i in self.N if i != h and i not in self.E)) == (
            quicksum(x[h, j, k] for j in self.N if j != h and j not in self.S))
                                      for h in self.N for k in self.K if h not in self.S and h not in self.E),
                                     name="c5_1")
        c5_2 = self.model.addConstrs(
            ((quicksum(x[i, h, k] for i in self.N if i != h)) == y[h, k] for h in self.T for k in self.K), name="c5_2")
        c5_3 = self.model.addConstrs(
            ((quicksum(x[h, j, k] for j in self.N if j != h)) == y[h, k] for h in self.T for k in self.K), name="c5_3")
        c5_4 = self.model.addConstrs((quicksum(y[i, k] for k in self.K) <= 1 for i in self.T), name="c5_4")

        c6 = self.model.addConstrs(
            (quicksum(self.c[i, j] * x[i, j, k] * 1 / self.vel for i in self.N for j in self.N if i != j) <= self.T_max
             for k in self.K), name="c6")

        # Time based flow constraints
        c7 = self.model.addConstrs((quicksum(q[i, j, k] for j in self.N if i != j and j not in self.S) -
                                    quicksum(q[j, i, k] for j in self.N if i != j and j not in self.E) ==
                                    quicksum(self.c[i, j] * x[i, j, k] for j in self.N if i != j)
                                    for k in self.K for i in self.N if i not in self.E), name='c7')
        # c8 = self.model.addConstrs((0 <= q[i,j,k] <= self.T_max*x[i,j,k] for i in self.N for j in self.N for k in self.K if i!=j and i not in self.E and j not in self.S), name='c8' )
        c8_1 = self.model.addConstrs((0 <= q[i, j, k] for i in self.N for j in self.N for k in self.K if
                                      i != j and i not in self.E and j not in self.S), name='c8_1')
        c8_2 = self.model.addConstrs(
            (q[i, j, k] <= self.T_max * x[i, j, k] for i in self.N for j in self.N for k in self.K if
             i != j and i not in self.E and j not in self.S), name='c8_2')
        c9 = self.model.addConstrs(
            (q[s, i, k] == self.f[s, i] * x[s, i, k] for i in self.T + self.D + self.E for s in self.S for k in self.K),
            name='c9')

        # Node based fuel constraints
        M = 1e6
        c10 = self.model.addConstrs(
            (r[j] - r[i] + self.f[i, j] <= M * (1 - x[i, j, k]) for i in self.T for j in self.T for k in self.K if
             i != j), name="c10")
        c11 = self.model.addConstrs(
            (r[j] - r[i] + self.f[i, j] >= -M * (1 - x[i, j, k]) for i in self.T for j in self.T for k in self.K if
             i != j), name="c11")
        c12 = self.model.addConstrs(
            (r[j] - self.L + self.f[i, j] <= M * (1 - x[i, j, k]) for i in self.D + self.S for j in
             self.T + self.D + self.E for k in self.K if i != j), name="c12")
        c13 = self.model.addConstrs(
            (r[j] - self.L + self.f[i, j] >= -M * (1 - x[i, j, k]) for i in self.D + self.S for j in
             self.T + self.D + self.E for k in self.K if i != j), name="c13")
        c14 = self.model.addConstrs(
            (r[i] - self.f[i, j] >= -M * (1 - x[i, j, k]) for i in self.S + self.T for j in self.D + self.E for k in
             self.K), name="c14")
        # c15 = self.model.addConstrs((0 <= r[i] <= self.L for i in self.T+self.E), name="c16")
        c15_1 = self.model.addConstrs((0 <= r[i] for i in self.T + self.E), name="c15_1")
        c15_2 = self.model.addConstrs((r[i] <= self.L for i in self.T + self.E), name="c15_2")
        c16 = self.model.addConstrs(
            (self.f[i, j] * x[i, j, k] <= self.L for i in self.S + self.D for j in self.D for k in self.K if i != j),
            name="c16")

    def solve(self):
        # self.model.params.Heuristics = 0.0  # %age of time use a heuristic solution
        # self.model.params.Cuts = 0  # Do not use cuts, except lazy constraints
        # model.params.MIPGapAbs = 0.0005
        # self.model.params.TimeLimit = 30
        self.model.Params.MIPGap = 1e-4
        self.model.optimize()

        return self.model

    def write_lp_and_sol_to_disk(self):
        #if not os.path.exists(self.instance_folder_path):
        #    os.makedirs(self.instance_folder_path)
        # Save runtime, because after writing the lp file,
        # runtime is lost. No idea why
        run_time = self.model.Runtime
        # Write both the LP file and the solution file
        self.model.write('Optimal' + '.lp')
        if self.model.status == GRB.OPTIMAL:
            self.model.write('Optimal' + '.sol')
            # Add runtime in the sol file as well.
            with open('Optimal' + '.sol', "a") as myfile:
                myfile.write('runtime:{}'.format(run_time))
        else:
            warnings.warn('No Optimal solution exists, so no solution file written to disk.')

    def read_best_paths(self):
        with open('Optimal.sol', newline='\n') as csvfile:
            reader = csv.reader((line.replace('  ', ' ')
                                 for line in csvfile), delimiter=' ')
            next(reader)  # skip header
            objective_value_line = next(reader)  # get the best objective value line
            rr = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", objective_value_line[-1])
            self.objective_val = float(rr[0])
            for line in reader:
                if len(line) == 2:
                    var = line[0]
                    value = line[1]
                    self.sol[var] = float(value)
                else:
                    _, self.runtime = line[0].split(':')
        self.compute_arcs_in_order()
        self.convert_to_nodes_in_order()
        self.create_tsp_corrected_tours()
        g_mapped_nodes_in_order_list = []
        for q in self.tspCorrectedNodesInOrderList:
            path = []
            for i in q:
                path.append(self.N_g_mapping[i])
            g_mapped_nodes_in_order_list.append(path)
        return g_mapped_nodes_in_order_list

    def compute_arcs_in_order(self):
        self.finalArcs = {k: [] for k in self.K}
        self.remainingFuel = {t: 0 for t in self.T}
        for i in self.sol:
            if self.sol[i] >= 0.9 and i[0] == 'x':
                x, y, k = i.split(',')
                x = x.replace("x[", "")
                k = k.replace("]", "")
                for q in range(math.ceil(self.sol[i])):
                    self.finalArcs[k].append((x, y))
            if self.sol[i] >= 0.9 and i[0] == 'r':
                x, y = i.split('[')
                y = y.replace("]", "")
                self.remainingFuel[y] = self.sol[i]

        # Create a graph for each robot
        G = {k: nx.MultiDiGraph() for k in self.K}
        # Add all nodes in the graph for each robot
        for k in self.K:
            G[k].add_nodes_from(self.N)
            G[k].add_edges_from(self.finalArcs[k])
            # print("Nodes in G["+k+"]: ", G[k].nodes(data=True))
            # print("Edges in G["+k+"]: ", G[k].edges(data=True))
        # Now compute the paths in the above graphs
        self.arcsInOrder = {k: [] for k in self.K}
        tempArcsInOrder = {k: [] for k in self.K}
        for k in self.K:
            tempArcsInOrder[k] = list(nx.edge_dfs(G[k], source=self.S[0]))
            for arc in tempArcsInOrder[k]:
                newArc = tuple((arc[0], arc[1]))
                self.arcsInOrder[k].append(newArc)

    def convert_to_nodes_in_order(self):
        self.nodesInOrder = {k: [] for k in self.K}
        for k in self.K:
            nodeBasedPath = [arc[0] for arc in self.arcsInOrder[k]]
            nodeBasedPath.append(self.arcsInOrder[k][-1][1])
            self.nodesInOrder[k] = nodeBasedPath[:]

    def get_fuel_spent(self):
        return self.fuel_spent

    def create_tsp_corrected_tours(self):
        self.tsp_corrected_tour_nodes = {k: [] for k in self.K}
        self.fuel_spent = {k: 0 for k in self.K}
        # Create data for TSP Solver
        for k in self.K:
            nodes = [node for node in self.nodesInOrder[k]]
            # Check if there are enough nodes for concorde to solve
            if nodes == ['S0', 'D0', 'E0'] or len(nodes) < 3:
                print ("No Nodes exist for Concorde to solve!")
                break
            X = [self.N_loc[node][0] for node in self.nodesInOrder[k]]
            Y = [self.N_loc[node][1] for node in self.nodesInOrder[k]]
            t_solver_map = {i: node for i, node in zip(range(len(nodes)),
                                                       self.nodesInOrder[k])}
            solver_t = TSPSolver.from_data(X, Y, norm="EUC_2D")
            tour_data = solver_t.solve()
            mapped_tour = [t_solver_map[i] for i in tour_data.tour]
            self.tsp_corrected_tour_nodes[k] = mapped_tour
            # Compute the new fuel spent
            for arc_0, arc_1 in zip(mapped_tour[:-1], mapped_tour[1:]):
                self.fuel_spent[k] += self.c[(arc_0, arc_1)]
        self.tspCorrectedNodesInOrderList = [list(i)
                                             for i in self.tsp_corrected_tour_nodes.values()]