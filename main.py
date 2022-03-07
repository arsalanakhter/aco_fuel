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
        form.form_submit_button(label='Submit')
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
        n_pools = 12
        n_ants = 2
        max_ant_fuel = 102
        max_mission_time = 290
        n_iterations = 26

    g = Graph(rng,  # random number generator
              n_depots,  # No. of depots
              n_tasks  # No. of Tasks
              )

    # Add a form to compute weight between any two nodes
    weight_form = st.sidebar.form(key='weight_form')
    n1 = weight_form.text_input(label='Node 1')
    n2 = weight_form.text_input(label='Node 2')
    calculate_weight_button = weight_form.form_submit_button(label='Calculate')
    st.sidebar.text(f'{g.adj_dist[int(n1), int(n2)]:0.2f}')


    st.header("ACO")
    aco_fuel_placeholder = st.empty()
    aco_path_placeholder = st.empty()
    aco_objective_value_placeholder = st.empty()
    plotter_aco = MapPlotter(g, n_ants)
    plotter_aco.init_plot()

    st.header("MILP")
    optimal_fuel_placeholder = st.empty()
    optimal_path_placeholder = st.empty()
    optimal_objective_value_placeholder = st.empty()
    plotter_optimal = MapPlotter(g, n_ants)
    plotter_optimal.init_plot()

    optimal_sol = TOPF_OptimalF7(g, n_ants, max_ant_fuel,
                                 max_mission_time, seed)
    optimal_sol.solve()
    optimal_sol.write_lp_and_sol_to_disk()
    optimal_best_paths = optimal_sol.read_best_paths()
    plotter_optimal.update(None, optimal_best_paths)  # None because
    # no pheromone information here
    optimal_fuel_placeholder.text(optimal_sol.get_fuel_spent())
    optimal_path_placeholder.text(optimal_best_paths)
    optimal_objective_value_placeholder.text(
        f'Obj Val: {optimal_sol.get_objective_value()}')



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
    pool_fuel, best_paths, best_obj_val = aco.run(n_iterations,  # number of iterations
                                    plotter_aco.update, g)
    aco_fuel_placeholder.text(pool_fuel)
    aco_path_placeholder.text(best_paths)
    aco_objective_value_placeholder.text(best_obj_val)


if __name__ == '__main__':
    main(streamlit_viz=1)
