from gurobipy import *
import copy

class TOPF_Optimal:

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
        self.S = self.D if len(self.D) == 1 else [self.D[0]]
        self.E = self.D if len(self.D) == 1 else [self.D[0]]
        self.N = self.T + self.D
        self.T_loc = {self.T[i]: g.nodes[g.depots + i] for i in range(g.tasks)}
        self.D_loc = {self.D[i]: g.nodes[i] for i in range(g.depots)}
        self.S_loc = self.D_loc[self.D[0]]
        self.E_loc = self.D_loc[self.D[0]]
        self.N_loc = {**self.D_loc, **self.T_loc}
        self.c = {(i1, j1): g.dist(i2, j2) for i1, i2 in zip(self.N, range(g.depots + g.tasks))
                                            for j1, j2 in zip(self.N, range(g.depots + g.tasks)) if i2 != j2}
        self.f = copy.deepcopy(self.c)
        self.arcs = [(i, j, k) for i in self.N for j in self.N if i != j for k in self.K]
        self.arc_ub = [len(self.N) if i[0] == 'D' or j[0] == 'D' else 1 for i, j, _ in self.arcs]
        self.init_model()

    def init_model(self):
        # Initialize the model
        self.model = Model(
            'F3TOBasic-' + '-Seed:' + str(self.thisSeed))
        # Decision variables and their bounds
        x = self.model.addVars(self.arcs, lb=0, ub=self.arc_ub, name="x", vtype=GRB.INTEGER)
        y = self.model.addVars(self.T, name="y", vtype=GRB.BINARY)
        r = self.model.addVars(self.N, lb=0, ub=self.L, vtype=GRB.CONTINUOUS, name="r")
        q = self.model.addVars(self.arcs, vtype=GRB.CONTINUOUS, name="q")

        # Objective function
        gamma = 0.0001
        objExpr1 = quicksum(y[i] for i in self.T)
        objExpr2 = quicksum(gamma * self.c[i, j] * x[i, j, k]
                            for k in self.K for i in self.N for j in self.N if i != j)
        objFun = objExpr1 - objExpr2
        self.model.setObjective(objFun, GRB.MAXIMIZE)

        # Constraints
        # For detail on what the constraints signify please see the
        # corresponding section in the report
        # c2_1 = self.model.addConstr((quicksum(x[s,j,k] for j in self.N
        # for k in self.K for s in self.S if j not in self.S) == self.noOfRobots), name="c2_1")
        # c2_2 = self.model.addConstr((quicksum(x[i,e,k] for i in self.N
        # for k in self.K for e in self.E if i!=e) == self.noOfRobots), name="c2_2")

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
            ((quicksum(x[i, h, k] for k in self.K for i in self.N if i != h)) == y[h] for h in self.T), name="c5_2")
        c5_3 = self.model.addConstrs(
            ((quicksum(x[h, j, k] for k in self.K for j in self.N if j != h)) == y[h] for h in self.T), name="c5_3")
        c5_4 = self.model.addConstrs((y[i] <= 1 for i in self.T), name="c5_4")

        c6 = self.model.addConstrs(
            (quicksum(self.c[i, j] * x[i, j, k] * 1 / self.vel for i in self.N for j in self.N if i != j) <= self.T_max
             for k in self.K), name="c6")

        # Time based flow constraints
        c7 = self.model.addConstrs((quicksum(q[i, j, k] for j in self.N if i != j and j not in self.S) -
                                    quicksum(q[j, i, k] for j in self.N if i != j and j not in self.E) ==
                                    quicksum(self.c[i, j] * x[i, j, k] for j in self.N if i != j)
                                    for k in self.K for i in self.N if i not in self.E), name='c7')
        # c8 = self.model.addConstrs((0 <= q[i,j,k] <= self.T_max*x[i,j,k] for i in self.N for j in
        # self.N for k in self.K if i!=j and i not in self.E and j not in self.S), name='c8' )
        c8_1 = self.model.addConstrs((0 <= q[i, j, k] for i in self.N for j in self.N for k in self.K if
                                      i != j and i not in self.E and j not in self.S), name='c8_1')
        c8_2 = self.model.addConstrs(
            (q[i, j, k] <= self.T_max * x[i, j, k] for i in self.N for j in self.N for k in self.K if
             i != j and i not in self.E and j not in self.S), name='c8_2')
        c9 = self.model.addConstrs(
            (q[s, i, k] == self.f[s, i] * x[s, i, k] for i in self.T + self.D + self.E for s in self.S for k in self.K
             if s != i),
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
             self.K if i != j), name="c14")
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
        self.model.Params.MIPGap = 1e-3
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
        self.model.write('Optimal' + '.sol')
        # Add runtime in the sol file as well.
        with open('Optimal' + '.sol', "a") as myfile:
            myfile.write('runtime:{}'.format(run_time))
