import plotly.graph_objects as go
import streamlit as st
import time
import numpy as np
import random


class MapPlotter:
    def __init__(self, graph, n_ants):
        self.graph = graph
        self.r = None
        self.layer_pheromones = None
        self.layer_best_path = None
        self.chart = None
        self.text = None
        self.df_distance = None
        self.distance_chart = None
        self.fig = go.Figure()
        self.n_ants = n_ants

    def init_plot(self):
        # Add Depots
        self.fig.add_trace(go.Scatter(
            x=self.graph.nodes[0:self.graph.depots, 0],
            y=self.graph.nodes[0:self.graph.depots, 1],
            mode='markers',
            marker=dict(color='red', size=13, symbol='square'),
            name='Depots',
            text=np.array(range(len(self.graph.nodes[0:self.graph.depots, 0])))
        ))
        # Add Tasks
        self.fig.add_trace(go.Scatter(
            x=self.graph.nodes[self.graph.depots:, 0],
            y=self.graph.nodes[self.graph.depots:, 1],
            mode='markers',
            marker=dict(color='blue', size=9),
            name='Tasks',
            text=self.graph.depots + np.array(range(len(self.graph.nodes[self.graph.depots:, 0])))
        ))

        # Add Best Paths (to be updated later)
        for n in range(self.n_ants):
            self.fig.add_trace(go.Scatter(
                x=[],
                y=[],
                line=dict(color=self._pick_random_color()),
                hoverinfo='none',
                showlegend=True,
                name='Best Path Ant '+str(n),
                mode='lines'))

        self.st_plotly_chart = st.plotly_chart(self.fig)

        # Empty plot to show the distance convergence
        # self.df_distance = pd.DataFrame({"Best distance": []})
        # self.distance_chart = st.line_chart(self.df_distance)
        # self.text = st.empty()

    def update(self, pheromone_matrix, best_paths):
        #self._update_pheromone_lines(pheromone_matrix)
        self._update_best_paths(best_paths)
        self.st_plotly_chart.plotly_chart(self.fig)
        time.sleep(1)

    #     lines_best_path = []
    #     start = [best_path[0].x, best_path[0].y]
    #     for node in best_path:
    #         lines_best_path.append({
    #             "start": start,
    #             "end": [node.x, node.y]
    #         })
    #         start = [node.x, node.y]
    #
    #     self.layer_pheromones.data = lines_pheromones
    #     self.layer_best_path.data = lines_best_path
    #     self.r.update()
    #     self.chart.pydeck_chart(self.r)
    #     self.distance_chart.add_rows({"Best distance": [distance]})
    #     self.text.text(f"Best distance = {distance:.2f}")
    #     time.sleep(0.01)
    #
    # def _get_init_view(self, lines):
    #     lat = [line["start"][1] for line in lines]
    #     lng = [line["start"][0] for line in lines]
    #     center_lat = (max(lat) - min(lat)) / 2 + min(lat)
    #     center_lng = (max(lng) - min(lng)) / 2 + min(lng)
    #     return pydeck.ViewState(latitude=center_lat, longitude=center_lng, zoom=self.zoom, max_zoom=10, pitch=0, bearing=0)
    #

    def _update_pheromone_lines(self, p_matrix):
        for i in range(len(p_matrix)):
            for j in range(len(p_matrix)):
                self.fig.add_trace(go.Scatter(
                    x=[self.graph.nodes[i, 0], self.graph.nodes[j, 0]],
                    y=[self.graph.nodes[i, 1], self.graph.nodes[j, 1]],
                    line=dict(width=p_matrix[i, j] / 100, color='grey'),
                    hoverinfo='none',
                    showlegend=False,
                    mode='lines'))

    def _update_best_paths(self, best_paths):
        '''

        :param best_paths: a list of lists of best paths for each ant/robot
        '''
        for n in range(self.n_ants):
            path_coords = self.graph.nodes[best_paths[n], :]
            self.fig.update_traces(selector=dict(name='Best Path Ant '+str(n)),
                                   x=path_coords[:, 0],
                                   y=path_coords[:, 1])

    def _pick_random_color(self):
        colors = [  'black',
                    'maroon', 	#800000
                    'red', 	    #ff0000
                    'purple', 	#800080
                    'fuchsia', 	#ff00ff
                    'green', 	#008000
                    'olive', 	#808000
                    # 'yellow', #ffff00
                    'navy', 	#000080
                    'blue', 	#0000ff
                    'teal', 	#008080
                    'aqua']
        # getting random color from list of hex colors
        return random.choice(colors)
