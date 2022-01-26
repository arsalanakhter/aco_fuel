import random as rnd
import math
import os
import sys
import json
import regex as re
from TO_SysPathGenerator import SysPathGenerator

class InstanceReader:

    def __init__(self, instance_string, path_to_data_folder=os.getcwd()):
        self.instance_string = instance_string
        self.path_to_data_folder = path_to_data_folder
        temp = [int(s) for s in re.findall(
            '\d+', instance_string)]  # extract numbers
        self.noOfRobots = temp[0]
        self.noOfDepots = temp[1]
        self.noOfTasks = temp[2]
        self.delta = temp[3]
        self.T_max = temp[4]
        self.iteration = temp[5]
        self.compute_data_filepath()
        self.readData()

    def compute_data_filepath(self):
        self.filePaths = SysPathGenerator(self.noOfRobots, self.noOfDepots, self.noOfTasks, 
                                            self.delta, self.T_max)
        self.instance_data_file = os.path.normpath(self.filePaths.instance_data_folder_path + \
                self.filePaths.instance_data_filename_prefix + 'Iter' + str(self.iteration)+ '.json')

    def readData(self):
        with open(self.instance_data_file, 'r') as f:
            self.json_data = json.load(f)
        self.iteration = self.json_data['iteration']
        self.thisSeed = self.json_data['thisSeed']
        self.noOfTasks = self.json_data['noOfTasks']
        self.noOfDepots = self.json_data['noOfDepots']
        self.noOfRobots = self.json_data['noOfRobots']
        self.arenaRadius = self.json_data['arenaRadius']
        self.K = self.json_data['K']
        self.T = self.json_data['T']
        self.D = self.json_data['D']
        self.S = self.json_data['S']
        self.E = self.json_data['E']
        self.N = self.json_data['N']

        self.L = self.json_data['L']
        self.delta = self.json_data['delta']
        self.vel = self.json_data['vel']
        self.T_max = self.json_data['T_max']
        #R = json_data['R']

        self.T_loc = self.json_data['T_loc']
        self.T_loc = {k: tuple(v) for k, v in self.T_loc.items()}

        self.D_loc = self.json_data['D_loc']
        self.D_loc = {k: tuple(v) for k, v in self.D_loc.items()}

        self.S_loc = self.json_data['S_loc']
        self.S_loc = {k: tuple(v) for k, v in self.S_loc.items()}

        self.E_loc = self.json_data['E_loc']
        self.E_loc = {k: tuple(v) for k, v in self.E_loc.items()}

        self.N_loc = self.json_data['N_loc']
        self.N_loc = {k: tuple(v) for k, v in self.N_loc.items()}

        self.edges = self.json_data['edges']
        self.edges = [tuple(n) for n in self.edges]
        self.c = self.json_data['c']
        self.c = {tuple(k.split(':')): v for k, v in self.c.items()}
        self.f = self.json_data['f']
        self.f = {tuple(k.split(':')): v for k, v in self.f.items()}

        self.arcs = self.json_data['arcs']
        self.arcs = [tuple(arc) for arc in self.arcs]

        self.arc_ub = self.json_data['arc_ub']
        self.arc_ub = {tuple(k.split(':')): v for k, v in self.arc_ub.items()}

        self.k_y = self.json_data['k_y']
        self.k_y = [tuple(arc) for arc in self.k_y]
        return self


def main():
    min_robots = 2
    max_robots = 2

    min_depots = 2
    max_depots = 2

    min_tasks = 5
    max_tasks = 5

    fuel_range_start = 50
    # fuel_range_end = int(math.ceil(2*100*math.sqrt(2)/5)*5)
    fuel_range_end = 50
    fuel_range_step = 5

    Tmax_range_start = 150
    # Tmax_range_end = int(math.ceil(2*100*math.sqrt(2)/10)*10)
    Tmax_range_end = 150
    Tmax_range_step = 10

    robots_range = list(range(min_robots, max_robots+1))
    depots_range = list(range(min_depots, max_depots+1))
    tasks_range = list(range(min_tasks, max_tasks+1))
    fuel_range = list(range(fuel_range_start, fuel_range_end +
                            fuel_range_step, fuel_range_step))
    Tmax_range = list(range(Tmax_range_start, Tmax_range_end +
                            Tmax_range_step, Tmax_range_step,))

    no_of_instances = 1
    path_to_data_folder = os.getcwd()
    instance_dictionary = {}

    for r in robots_range:
        for d in depots_range:
            for t in tasks_range:
                for f in fuel_range:
                    for tmax in Tmax_range:
                        instance_folder_path_suffix = \
                            '/data' + \
                            '/R' + str(r) + \
                            '/D' + str(d) + \
                            '/T' + str(t) + \
                            '/F' + str(f) + \
                            '/Tmax' + str(tmax)
                        instance_folder_path = os.path.normpath(
                            path_to_data_folder + instance_folder_path_suffix)
                        instance_filename_prefix = '/R' + str(r) + \
                            'D' + str(d) + \
                            'T' + str(t) + \
                            'F' + str(f) + \
                            'Tmax' + str(tmax)
                        for it in range(no_of_instances):
                            curr_instance_filename = instance_filename_prefix + \
                                'Iter' + str(it) + '.json'
                            file_path = os.path.normpath(
                                instance_folder_path+curr_instance_filename)
                            instance = InstanceReader(file_path)
                            instance_dictionary[curr_instance_filename[1:-5]
                                                ] = instance.readData()

    # Print the seed of the last read file.
    print(instance_dictionary[curr_instance_filename[1:-5]].thisSeed)


if __name__ == "__main__":
    main()
