from Graph import Graph
from TOPF_ACO_Shared import TOPF_ACO_Shared
from plotter import MapPlotter
from streamlit_print import st_stdout

from utils import fuelf_linear, timef_linear, pheromonef_lay

from numpy.random import default_rng
import streamlit as st


def main(streamlit_viz = 0):

    st.title("Ant Colony Optimization with Fuel")
    st.write("Create a graph with task an depot nodes. Display the pheromones and best path.")
    seed = 12345
    rng = default_rng(seed)

    if streamlit_viz:
        n_depots = st.sidebar.slider("Number of depots", 1, 10, 1)
        n_tasks = st.sidebar.slider("Number of tasks", 1, 10, 1)
        n_pools = st.sidebar.slider("Number of ant pools", 1, 5, 1)
        n_ants = st.sidebar.slider("Number of ants per pool", 1, 10, 1)

    else:
        n_depots = 10
        n_tasks = 10
        n_pools = 1
        n_ants = 3

    g = Graph(rng,  # random number generator
              n_depots,  # No. of depots
              n_tasks  # No. of Tasks
              )

    plotter = MapPlotter(g)
    plotter.init_plot()

    aco = TOPF_ACO_Shared(
        rng,       # random number generator
        n_pools,   # pools
        n_ants,    # ants per pool
        g,         # graph
        0,         # start_node
        fuelf_linear,  # fuel function
        timef_linear,  # time function
        100.0,         # max_time
        None,          # heuristic function
        pheromonef_lay  # pheromone function
    )
    st.header("Console Output:")
    with st_stdout("code"):
        aco.run(10  # number of iterations
            )


if __name__ == '__main__':
    main(streamlit_viz=1)
