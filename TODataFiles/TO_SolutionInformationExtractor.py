# TODO: Extract information from the combination of instance and solution.
#  That can include functions which extract information such as
# - Given a node, how far is the closest task/depot?
# - Given a node, How far is the farthest task/depot?
# - Given a solution, for each node, did the robot pick a task node or a depot
# node, given the fuel at the node?

from pprint import pprint
import random as rnd
import math
import numpy as np
import os
import regex as re
import csv
from TO_InstanceReader import InstanceReader
from TO_SolutionReader import Solution_Reader


class SolutionInformationExtractor:

    def __init__(self, instance, sol):
        self.instance = instance
        self.sol = sol

    def recharge_recharge_task_frequency(self):
        self.recharge_recharge_count = 0
        self.recharge_task_count = 0
        for k in self.instance.K:
            it1 = iter(self.sol.nodesInOrder[k])
            it2 = iter(self.sol.nodesInOrder[k])
            it2.__next__()
            for n1, n2 in zip(it1, it2):
                if n1 in self.instance.D:
                    if n2 in self.instance.D:
                        self.recharge_recharge_count += 1
                    elif n2 in self.instance.T:
                        self.recharge_task_count += 1
                # Deal the edge cases for start/end nodes here
                if n1 in self.instance.S:
                    if n2 in self.instance.D and n2 not in self.instance.D[0]:
                        self.recharge_recharge_count += 1
                    elif n2 in self.instance.T:
                        self.recharge_task_count += 1

                if n2 in self.instance.E:
                    if n1 in self.instance.D and n1 not in self.instance.D[0]:
                        self.recharge_recharge_count += 1


    def distance_travelled_calculator(self):
        distance_all_robots = []
        for k in self.instance.K:
            route = self.sol.nodesInOrder[k]
            n1 = route[0]
            distance = 0
            for n2 in route[1:]:
                distance += self.instance.c[n1, n2]

            distance_all_robots.append(distance)

        return distance_all_robots


'''
    def compute_data_filepath(self):
        instance_data_folder_path_suffix = \
            '/data' + \
            '/R' + str(self.noOfRobots) + \
            '/D' + str(self.noOfDepots) + \
            '/T' + str(self.noOfTasks) + \  
            '/F' + str(self.L) + \
            '/Tmax' + str(self.T_max)
        instance_data_folder_path = \
            self.path_to_data_folder + instance_data_folder_path_suffix
        instance_data_filename_prefix = \
            '\\R' + str(self.noOfRobots) + \
            'D' + str(self.noOfDepots) + \
            'T' + str(self.noOfTasks) + \
            'F' + str(self.L) + \
            'Tmax' + str(self.T_max) + \
            'Iter' + str(self.iteration)
        self.instance_data_file = os.path.normpath(
            instance_data_folder_path + instance_data_filename_prefix + '.json')

    def compute_sol_filepath(self):
        instance_sol_folder_path_suffix = \
            '/sol' + \
            '/R' + str(self.noOfRobots) + \
            '/D' + str(self.noOfDepots) + \
            '/T' + str(self.noOfTasks) + \
            '/F' + str(self.L) + \
            '/Tmax' + str(self.T_max)
        instance_sol_folder_path = \
            self.path_to_data_folder + instance_sol_folder_path_suffix
        instance_sol_filename_prefix = \
            '\\R' + str(self.noOfRobots) + \
            'D' + str(self.noOfDepots) + \
            'T' + str(self.noOfTasks) + \
            'F' + str(self.L) + \
            'Tmax' + str(self.T_max) + \
            'Iter' + str(self.iteration)
        self.instance_sol_file = os.path.normpath(
            instance_sol_folder_path + instance_sol_filename_prefix + '.sol')
'''


def main():
    # instance_prefix = 'R3D2T3F150Tmax600Iter'
    instance_prefix = 'R3D3T7F150Tmax600Iter'
    no_of_instances = 5
    for i in range(no_of_instances):
        instance_name = instance_prefix + str(i)
        instance = InstanceReader(instance_name)
        sol = Solution_Reader(instance_name)
        # pprint(sol.nodesInOrder)
        sol_info = SolutionInformationExtractor(instance, sol)
        sol_info.recharge_recharge_task_frequency()
        # print(sol_info.recharge_recharge_count)
        # print(sol_info.recharge_task_count)
        # curr_instance_filename = instance_prefix + 'Iter' + str(i) + '.json'
        # file_path = os.path.normpath(instance_folder_path + curr_instance_filename)

        distance_travelled = sol_info.distance_travelled_calculator()

        with open('analysis/data.csv', 'a') as csvFile:
            writer = csv.writer(csvFile)
            row = [instance_name, sol_info.recharge_task_count, sol_info.recharge_recharge_count]
            for x in distance_travelled:
                row.append(x)
            writer.writerow(row)
        csvFile.close()


if __name__ == "__main__":
    main()
