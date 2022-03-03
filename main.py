from Graph import Graph
from TOPF_ACO_Shared import TOPF_ACO_Shared
from plotter import MapPlotter
from streamlit_print import st_stdout

from utils import fuelf_linear, timef_linear, pheromonef_lay

from numpy.random import default_rng
import streamlit as st

from TOPF_OptimalF7 import TOPF_OptimalF7
from TOPF_Optimal import TOPF_OptimalF6


def main(streamlit_viz=0):
    st.title("Ant Colony Optimization with Fuel")
    st.write("Create a graph with task an depot nodes. Display the "
             "pheromones and best path.")
    seed = 12345
    rng = default_rng(seed)

    if streamlit_viz:
        form = st.sidebar.form(key='sidebar_form')
        submit_button = form.form_submit_button(label='Submit')
        n_depots = form.slider("Number of depots", 1, 10, 1)
        n_tasks = form.slider("Number of tasks", 1, 10, 1)
        n_pools = form.slider("Number of ant pools", 1, 50, 1)
        n_ants = form.slider("Number of ants per pool", 1, 10, 1)
        max_ant_fuel = form.slider("Maximum Ant Fuel", 1, 500,
                                   1)
        max_mission_time = form.slider("Maximum mission time", 1,
                                       500, 1)
        n_iterations = form.slider("Number Of ACO Iterations", 1,
                                   50, 1)

    else:
        n_depots = 3
        n_tasks = 7
        n_pools = 17
        n_ants = 2
        max_ant_fuel = 323
        max_mission_time = 384
        n_iterations = 1

    g = Graph(rng,  # random number generator
              n_depots,  # No. of depots
              n_tasks  # No. of Tasks
              )

    st.header("ACO")
    aco_fuel_placeholder = st.empty()
    aco_path_placeholder = st.empty()
    plotter_aco = MapPlotter(g, n_ants)
    plotter_aco.init_plot()

    st.header("MILP")
    optimal_fuel_placeholder = st.empty()
    optimal_path_placeholder = st.empty()
    plotter_optimal = MapPlotter(g, n_ants)
    plotter_optimal.init_plot()

    st.header("TSP-Corrected MILP")
    optimal_fuel_placeholder2 = st.empty()
    optimal_path_placeholder2 = st.empty()
    plotter_optimal2 = MapPlotter(g, n_ants)
    plotter_optimal2.init_plot()


    optimal_sol = TOPF_OptimalF7(g, n_ants, max_ant_fuel,
                                 max_mission_time, seed)
    optimal_sol.solve()
    optimal_sol.write_lp_and_sol_to_disk()
    optimal_best_paths, optimal_best_paths_before_tsp_correction = \
        optimal_sol.read_best_paths()

    plotter_optimal.update(None, optimal_best_paths_before_tsp_correction)
    # None because no pheromone information here
    #plotter_optimal2.update(None, optimal_best_paths)

    fuel_spent, fuel_spent_before_tsp_correction = optimal_sol.get_fuel_spent()
    optimal_fuel_placeholder.text(fuel_spent_before_tsp_correction)
    #optimal_fuel_placeholder2.text(fuel_spent)

    optimal_path_placeholder.text(optimal_best_paths_before_tsp_correction)
    #optimal_path_placeholder2.text(optimal_best_paths)



    aco = TOPF_ACO_Shared(
        rng,  # random number generator
        n_pools,  # pools
        n_ants,  # ants per pool
        g,  # graph
        0,  # start_node
        fuelf_linear,  # fuel function
        timef_linear,  # time function
        max_ant_fuel,  # maximum fuel for each ant
        max_mission_time,  # max_time
        None,  # heuristic function
        pheromonef_lay  # pheromone function
    )
    # st.header("Console Output:")
    # with st_stdout("code"):
    pool_fuel, best_paths = aco.run(n_iterations,  # number of iterations
                                    plotter_aco.update, g)
    aco_fuel_placeholder.text(pool_fuel)
    aco_path_placeholder.text(best_paths)


if __name__ == '__main__':
    main(streamlit_viz=0)
