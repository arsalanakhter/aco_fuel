# The class takes in a string for an instance, and generates folder paths and
# instance and solution filenames
import regex as re
import os


class SysPathGenerator:

    def __init__(self, noOfRobots, noOfDepots, noOfTasks, delta, Tmax, path_to_working_dir=os.getcwd()):
        self.path_to_working_dir = path_to_working_dir
        #temp = [int(s) for s in re.findall(
        #    '\d+', instance_string)]  # extract numbers
        self.noOfRobots = noOfRobots
        self.noOfDepots = noOfDepots
        self.noOfTasks = noOfTasks
        self.delta = delta
        self.T_max = Tmax
        self.compute_data_filepath()
        self.compute_sol_filepath()

    def compute_data_filepath(self):
        instance_data_folder_path_suffix = \
            '/data' + \
            '/R' + str(self.noOfRobots) + \
            '/D' + str(self.noOfDepots) + \
            '/T' + str(self.noOfTasks) + \
            '/Delta' + str(self.delta) + \
            '/Tmax' + str(self.T_max)
        self.instance_data_folder_path = \
            os.path.normpath(self.path_to_working_dir +
                             instance_data_folder_path_suffix)
        self.instance_data_filename_prefix = \
            '/R' + str(self.noOfRobots) + \
            'D' + str(self.noOfDepots) + \
            'T' + str(self.noOfTasks) + \
            'Delta' + str(self.delta) + \
            'Tmax' + str(self.T_max)
        self.instance_data_file = os.path.normpath(
            self.instance_data_folder_path + self.instance_data_filename_prefix)

    def compute_sol_filepath(self):
        instance_sol_folder_path_suffix = \
            '/sol' + \
            '/R' + str(self.noOfRobots) + \
            '/D' + str(self.noOfDepots) + \
            '/T' + str(self.noOfTasks) + \
            '/Delta' + str(self.delta) + \
            '/Tmax' + str(self.T_max)
        self.instance_sol_folder_path = os.path.normpath(
            self.path_to_working_dir + instance_sol_folder_path_suffix)
        self.instance_sol_filename_prefix = \
            'R' + str(self.noOfRobots) + \
            'D' + str(self.noOfDepots) + \
            'T' + str(self.noOfTasks) + \
            'Delta' + str(self.delta) + \
            'Tmax' + str(self.T_max)
        self.instance_sol_file = os.path.normpath(
            self.instance_sol_folder_path + self.instance_sol_filename_prefix)
