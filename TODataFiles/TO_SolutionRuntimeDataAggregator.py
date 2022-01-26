import os
import csv
import numpy as np

from TO_SolutionReader import Solution_Reader


class SolutionRuntimeDataAggregator:

    def __init__(self, formulations_list,
                        no_of_robots,
                        no_of_depots_list,
                        no_of_tasks_list,
                        delta_param_list,
                        Tmax_param_list,
                        iterations_list,
                        path_to_data_folder=os.getcwd()):

        self.formulations_list = formulations_list
        self.no_of_robots = no_of_robots
        self.no_of_depots_list = no_of_depots_list
        self.no_of_tasks_list = no_of_tasks_list
        self.delta_param_list = delta_param_list
        self.Tmax_param_list = Tmax_param_list
        self.iterations_list = iterations_list
                       
        self.solution_runtimes = {}
        for f in self.formulations_list:
            self.solution_runtimes['F'+str(f)] = {}
            for r in self.no_of_robots:
                self.solution_runtimes['F'+str(f)]['R'+str(r)] = {}
                for d in self.no_of_depots_list:
                    self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)] = {}
                    for t in self.no_of_tasks_list:
                        self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)]['T'+str(t)] = {}
                        for delta in self.delta_param_list:
                            self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)]['T'+str(t)]['delta'+str(delta)] = {}
                            for tmax in self.Tmax_param_list:
                                self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)]['T'+str(t)]['delta'+str(delta)]['Tmax'+str(tmax)] = {}
                                for i in self.iterations_list:
                                    this_instance_string = 'F' + str(f) + \
                                        'R' + str(r) + 'D' + str(d) + \
                                        'T' + str(t) + 'delta' + str(delta) + \
                                        'Tmax' + str(tmax) + 'Iter' + str(i)
                                    this_sol = Solution_Reader(this_instance_string)
                                    self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)]['T'+str(t)]['delta'+str(delta)]['Tmax'+str(tmax)]['Iter'+str(i)] = this_sol.runtime


    def write_to_csv(self):
        self.resultsFile = os.path.normpath(os.getcwd()+'/aggregatedDataR'+str(self.no_of_robots[0])+'.csv')
        with open(self.resultsFile, 'w+') as results_file:
            result_writer = csv.writer(results_file, delimiter=',', lineterminator='\n')
            # Write row1
            row1 = [' ',' ',' ']
            row2 = [' ',' ',' ']
            row3 = [' ',' ',' ']
            for formulation in self.formulations_list:
                row1 = row1 + ['F'+str(formulation) for i in range (len(self.no_of_depots_list)*len(self.no_of_tasks_list))]
                # Write row2
                for d in self.no_of_depots_list:
                    row2 = row2 + ['D'+str(d) for i in range (len(self.no_of_tasks_list))]
                    # Write row3
                    for t in self.no_of_tasks_list:
                        row3 = row3 + ['T'+str(t)]
            result_writer.writerow(row1)
            result_writer.writerow(row2)
            result_writer.writerow(row3)

            for r in self.no_of_robots:
                for tmax in self.Tmax_param_list:
                    for delta in self.delta_param_list:
                        for i in self.iterations_list:
                            row_tbw = ['Tmax'+str(tmax), 'tau'+str(delta), 'Iter'+str(i)]
                            for f in self.formulations_list:
                                for d in self.no_of_depots_list:
                                    for t in self.no_of_tasks_list:
                                        row_tbw = row_tbw + [str(self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)]['T'+str(t)]['delta'+str(delta)]['Tmax'+str(tmax)]['Iter'+str(i)])]
                            result_writer.writerow(row_tbw)


    def write_min_avg_max_to_csv(self):
        self.resultsFile = os.path.normpath(os.getcwd()+'/aggregatedDataMinAvgMaxR'+str(self.no_of_robots[0])+'.csv')
        with open(self.resultsFile, 'w+') as results_file:
            result_writer = csv.writer(results_file, delimiter=',',lineterminator='\n')
            # Write row1
            row1 = [' ',' ',' ']
            for formulation in self.formulations_list:
                for d in self.no_of_depots_list:
                    for t in self.no_of_tasks_list:
                        row1 = row1 + ['F'+str(formulation) + 'D'+str(d) + 'T'+str(t)]
            result_writer.writerow(row1)

            for r in self.no_of_robots:
                for tmax in self.Tmax_param_list:
                    for delta in self.delta_param_list:
                        row_tbw_min = ['Tmax'+str(tmax), '\\tau'+str(delta), 'Min']
                        row_tbw_avg = ['Tmax'+str(tmax), '\\tau'+str(delta), 'Avg']
                        row_tbw_std = ['Tmax'+str(tmax), '\\tau'+str(delta), 'StdDev']
                        row_tbw_max = ['Tmax'+str(tmax), '\\tau'+str(delta), 'Max']
                        #row_tbw_min = [' ']
                        #row_tbw_avg = [' ']
                        #row_tbw_std = [' ']
                        #row_tbw_max = [' ']
                        for f in self.formulations_list:
                            for d in self.no_of_depots_list:
                                for t in self.no_of_tasks_list:
                                    iter_min = 0
                                    iter_avg = 0
                                    iter_std = 0
                                    iter_max = 0
                                    iter_data = []
                                    for i in self.iterations_list:
                                        iter_data = iter_data + [self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)]['T'+str(t)]['delta'+str(delta)]['Tmax'+str(tmax)]['Iter'+str(i)]]
                                    iter_min = min(iter_data)
                                    iter_avg = '{:.2f}'.format(np.mean([float(i) for i in iter_data]))
                                    iter_std = '{:.2f}'.format(np.std([float(i) for i in iter_data]))
                                    iter_max = max(iter_data)
                                    row_tbw_min = row_tbw_min + [iter_min]
                                    row_tbw_avg = row_tbw_avg + [iter_avg]
                                    row_tbw_std = row_tbw_std + [iter_std]
                                    row_tbw_max = row_tbw_max + [iter_max]
                        result_writer.writerow(row_tbw_min)
                        result_writer.writerow(row_tbw_avg)
                        result_writer.writerow(row_tbw_std)
                        result_writer.writerow(row_tbw_max)



    def write_latex_table(self):
        self.resultsFile = os.path.normpath(os.getcwd()+'/latexTableR'+str(self.no_of_robots[0])+'.txt')
        with open(self.resultsFile, 'w+') as results_file:
            string = """
                        %%%%%%%%%%%%%%%%%%%%%%%%%
                        \\begin{table*}
                        \\centering
                        \\resizebox{\\textwidth}{!}{%
                        \\begin{tabular}{ccccccccccccccccccc} 
                        \\toprule
                        \\multicolumn{3}{c}{}&
                        \\multicolumn{4}{c}{F1}&
                        \\multicolumn{4}{c}{F2}& 
                        \\multicolumn{4}{c}{F3}&
                        \\multicolumn{4}{c}{F4}\\\\

                        \\cmidrule(lr){4-7}
                        \\cmidrule(lr){8-11}
                        \\cmidrule(lr){12-15}
                        \\cmidrule(lr){16-19}

                        \\multicolumn{3}{c}{No. Of Depots}&
                        \\multicolumn{2}{c}{2}&
                        \\multicolumn{2}{c}{3}&
                        \\multicolumn{2}{c}{2}&
                        \\multicolumn{2}{c}{3}& 
                        \\multicolumn{2}{c}{2}&
                        \\multicolumn{2}{c}{3}&
                        \\multicolumn{2}{c}{2}&
                        \\multicolumn{2}{c}{3}\\\\

                        \\cmidrule(lr){4-5}
                        \\cmidrule(lr){6-7}
                        \\cmidrule(lr){8-9}
                        \\cmidrule(lr){10-11}
                        \\cmidrule(lr){12-13}
                        \\cmidrule(lr){14-15}
                        \\cmidrule(lr){16-17}
                        \\cmidrule(lr){18-19}



                        \\multicolumn{3}{c}{No. Of Tasks}
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10\\\\

                        \\midrule
            """
            results_file.write(string)
            result_writer = csv.writer(results_file, delimiter='&',lineterminator='\n')
            for r in self.no_of_robots:
                for tmax in self.Tmax_param_list:
                    for fuel in self.delta_param_list:
                        row_tbw_min = ['Tmax'+str(tmax), '$\\tau$'+str(fuel), 'Min']
                        row_tbw_avg = ['Tmax'+str(tmax), '$\\tau$'+str(fuel), 'Avg']
                        row_tbw_std = ['Tmax'+str(tmax), '$\\tau$'+str(fuel), 'Std']
                        row_tbw_max = ['Tmax'+str(tmax), '$\\tau$'+str(fuel), 'Max']
                        #row_tbw_min = [' ']
                        #row_tbw_avg = [' ']
                        #row_tbw_std = [' ']
                        #row_tbw_max = [' ']
                        for f in self.formulations_list:
                            for d in self.no_of_depots_list:
                                for t in self.no_of_tasks_list:
                                    iter_min = 0
                                    iter_avg = 0
                                    iter_std = 0
                                    iter_max = 0
                                    iter_data = []
                                    for i in self.iterations_list:
                                        iter_data = iter_data + [self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)]['T'+str(t)]['delta'+str(fuel)]['Tmax'+str(tmax)]['Iter'+str(i)]]
                                    iter_min = min(iter_data)
                                    iter_avg = '{:.2f}'.format(np.mean([float(i) for i in iter_data]))
                                    iter_std = '{:.2f}'.format(np.std([float(i) for i in iter_data]))
                                    iter_max = max(iter_data)
                                    row_tbw_min = row_tbw_min + [iter_min]
                                    row_tbw_avg = row_tbw_avg + [iter_avg]
                                    row_tbw_std = row_tbw_std + [iter_std]
                                    row_tbw_max = row_tbw_max + [iter_max]
                        result_writer.writerow(row_tbw_min)
                        results_file.write("\\\\")
                        result_writer.writerow(row_tbw_avg)
                        results_file.write("\\\\")
                        result_writer.writerow(row_tbw_std)
                        results_file.write("\\\\")
                        result_writer.writerow(row_tbw_max)
                        results_file.write("\\\\")
                        results_file.write("\\cmidrule(lr){3-19}")
                    results_file.write("\\cmidrule(lr){2-19}")
            string = """
                        \\bottomrule
                        \\end{tabular}
                    }"""
            results_file.write(string)
            results_file.write('\\caption{Runtime for'+str(len(self.iterations_list))+'random instances - No. of Robots = '+str(self.no_of_robots[0])+'}')
            results_file.write('\\label{tab:AllRuntimesR='+str(self.no_of_robots[0])+'}')
            results_file.write('\\end{table*}')
            results_file.write('%%%%%%%%%%%%%%%%%%%%%')



    def write_latex_table_avg_only(self):
        self.resultsFile = os.path.normpath(os.getcwd()+'/latexTableAvgOnlyR'+str(self.no_of_robots[0])+'.txt')
        with open(self.resultsFile, 'w+') as results_file:
            string = """
                        %%%%%%%%%%%%%%%%%%%%%%%%%
                        \\begin{table*}
                        \\centering
                        \\resizebox{\\textwidth}{!}{%
                        \\begin{tabular}{ccccccccccccccccccc} 
                        \\toprule
                        \\multicolumn{3}{c}{}&
                        \\multicolumn{4}{c}{F1}&
                        \\multicolumn{4}{c}{F2}& 
                        \\multicolumn{4}{c}{F3}&
                        \\multicolumn{4}{c}{F4}\\\\

                        \\cmidrule(lr){4-7}
                        \\cmidrule(lr){8-11}
                        \\cmidrule(lr){12-15}
                        \\cmidrule(lr){16-19}

                        \\multicolumn{3}{c}{No. Of Depots}&
                        \\multicolumn{2}{c}{2}&
                        \\multicolumn{2}{c}{3}&
                        \\multicolumn{2}{c}{2}&
                        \\multicolumn{2}{c}{3}& 
                        \\multicolumn{2}{c}{2}&
                        \\multicolumn{2}{c}{3}&
                        \\multicolumn{2}{c}{2}&
                        \\multicolumn{2}{c}{3}\\\\

                        \\cmidrule(lr){4-5}
                        \\cmidrule(lr){6-7}
                        \\cmidrule(lr){8-9}
                        \\cmidrule(lr){10-11}
                        \\cmidrule(lr){12-13}
                        \\cmidrule(lr){14-15}
                        \\cmidrule(lr){16-17}
                        \\cmidrule(lr){18-19}



                        \\multicolumn{3}{c}{No. Of Tasks}
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10
                        & 5 & 10\\\\

                        \\midrule
            """
            results_file.write(string)
            result_writer = csv.writer(results_file, delimiter='&',lineterminator='\n')
            for r in self.no_of_robots:
                for tmax in self.Tmax_param_list:
                    for fuel in self.delta_param_list:
                        #row_tbw_min = ['Tmax'+str(tmax), '$\\tau$'+str(fuel), 'Min']
                        row_tbw_avg = ['Tmax'+str(tmax), '$\\tau$'+str(fuel), 'Avg']
                        #row_tbw_std = ['Tmax'+str(tmax), '$\\tau$'+str(fuel), 'Std']
                        #row_tbw_max = ['Tmax'+str(tmax), '$\\tau$'+str(fuel), 'Max']
                        #row_tbw_min = [' ']
                        #row_tbw_avg = [' ']
                        #row_tbw_std = [' ']
                        #row_tbw_max = [' ']
                        for f in self.formulations_list:
                            for d in self.no_of_depots_list:
                                for t in self.no_of_tasks_list:
                                    #iter_min = 0
                                    iter_avg = 0
                                    #iter_std = 0
                                    #iter_max = 0
                                    iter_data = []
                                    for i in self.iterations_list:
                                        iter_data = iter_data + [self.solution_runtimes['F'+str(f)]['R'+str(r)]['D'+str(d)]['T'+str(t)]['delta'+str(fuel)]['Tmax'+str(tmax)]['Iter'+str(i)]]
                                    #iter_min = min(iter_data)
                                    iter_avg = '{:.2f}'.format(np.mean([float(i) for i in iter_data]))
                                    #iter_std = '{:.2f}'.format(np.std([float(i) for i in iter_data]))
                                    #iter_max = max(iter_data)
                                    #row_tbw_min = row_tbw_min + [iter_min]
                                    row_tbw_avg = row_tbw_avg + [iter_avg]
                                    #row_tbw_std = row_tbw_std + [iter_std]
                                    #row_tbw_max = row_tbw_max + [iter_max]
                        #result_writer.writerow(row_tbw_min)
                        #results_file.write("\\\\")
                        result_writer.writerow(row_tbw_avg)
                        results_file.write("\\\\")
                        #result_writer.writerow(row_tbw_std)
                        #results_file.write("\\\\")
                        #result_writer.writerow(row_tbw_max)
                        #results_file.write("\\\\")
                        results_file.write("\\cmidrule(lr){3-19}")
                    results_file.write("\\cmidrule(lr){2-19}")
            string = """
                        \\bottomrule
                        \\end{tabular}
                    }"""
            results_file.write(string)
            results_file.write('\\caption{Runtime for '+str(len(self.iterations_list))+' random instances - No. of Robots = '+str(self.no_of_robots[0])+'}')
            results_file.write('\\label{tab:AllRuntimesR='+str(self.no_of_robots[0])+'}')
            results_file.write('\\end{table*}')
            results_file.write('%%%%%%%%%%%%%%%%%%%%%')



def main():
    formulations_list = [1,2,3,4]
    no_of_robots_list = [4] # We can only put one robot number here.
    no_of_depots_list =[1, 2, 3]
    no_of_tasks_list = [5 , 10]
    delta_param_list = [50, 75, 100, 125, 150]
    Tmax_param_list = [50, 75, 150, 300, 450, 600]
    iterations_list = [i for i in range(10)]

    agg = SolutionRuntimeDataAggregator(
                        formulations_list,
                        no_of_robots_list,
                        no_of_depots_list,
                        no_of_tasks_list,
                        delta_param_list,
                        Tmax_param_list,
                        iterations_list)

    agg.write_to_csv()
    print('All data written to csv')
    agg.write_min_avg_max_to_csv()
    print('Min-Avg_Max data written to csv')
    agg.write_latex_table()
    print('latex table written')
    agg.write_latex_table_avg_only()
    print('latex table written (with averages only)')

if __name__ == "__main__":
    main()
