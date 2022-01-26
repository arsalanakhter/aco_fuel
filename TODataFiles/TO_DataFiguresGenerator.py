import pandas as pd
import plotly.offline as py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


class DataFiguresGenerator:

    def __init__(self, formulations_list,
                        no_of_robots_list,
                        no_of_depots_list,
                        no_of_tasks_list,
                        delta_param_list,
                        Tmax_param_list,
                        iterations_list,
                        path_to_data_folder=os.getcwd()):

        self.formulations_list = formulations_list
        self.no_of_robots_list = no_of_robots_list
        self.no_of_depots_list = no_of_depots_list
        self.no_of_tasks_list = no_of_tasks_list
        self.delta_param_list = delta_param_list
        self.Tmax_param_list = Tmax_param_list
        self.iterations_list = iterations_list


    def compute_Tmax_plots(self):
        for d in self.no_of_depots_list:
            for tau in self.delta_param_list:
                self.compute_single_Tmax_plot(d, tau)

    def compute_tau_plots(self):
        for d in self.no_of_depots_list:
            for tmax in self.Tmax_param_list:
                self.compute_single_tau_plot(d, tmax)

    def compute_single_Tmax_plot(self, d, tau):
        r=self.no_of_robots_list[0] # No of robots
        # Pick the data for this plot only
        row_fields = [' ', ' .1', ' .2']
        for f in self.formulations_list:
            for t in self.no_of_tasks_list:
                row_fields.append('F'+str(f)+'D'+str(d)+'T'+str(t))
        col_fields = ['Avg']
        df = pd.read_csv('aggregatedDataMinAvgMaxR'+str(r)+'.csv', usecols=row_fields, index_col=False)
        print(df[df[' .2'].str.contains(col_fields[0])])
        fig = self.draw_figure()
        y_max = 0
        tasks_reversed = self.no_of_tasks_list[::-1]
        for t in tasks_reversed: 
            F1trace = self.F1_trace()
            ydata = df[df[' .2'].str.contains(col_fields[0])]
            ydata = ydata[ydata[' .1'].isin(['\\tau'+str(tau)])]['F'+str(self.formulations_list[0])+'D'+str(d)+'T'+str(t)].tolist()
            ydata_max = max(ydata)
            if ydata_max > y_max:
                y_max = ydata_max
            F1trace.update(x=self.Tmax_param_list, y=ydata)

            F2trace = self.F2_trace()
            ydata = df[df[' .2'].str.contains(col_fields[0])]
            ydata = ydata[ydata[' .1'].isin(['\\tau'+str(tau)])]['F'+str(self.formulations_list[1])+'D'+str(d)+'T'+str(t)].tolist()
            ydata_max = max(ydata)
            if ydata_max > y_max:
                y_max = ydata_max
            F2trace.update(x=self.Tmax_param_list, y=ydata)

            F3trace = self.F3_trace()
            ydata = df[df[' .2'].str.contains(col_fields[0])]
            ydata = ydata[ydata[' .1'].isin(['\\tau'+str(tau)])]['F'+str(self.formulations_list[2])+'D'+str(d)+'T'+str(t)].tolist()
            ydata_max = max(ydata)
            if ydata_max > y_max:
                y_max = ydata_max
            F3trace.update(x=self.Tmax_param_list, y=ydata)

            F4trace = self.F4_trace()
            ydata = df[df[' .2'].str.contains(col_fields[0])]
            ydata = ydata[ydata[' .1'].isin(['\\tau'+str(tau)])]['F'+str(self.formulations_list[3])+'D'+str(d)+'T'+str(t)].tolist()
            ydata_max = max(ydata)
            if ydata_max > y_max:
                y_max = ydata_max
            F4trace.update(x=self.Tmax_param_list, y=ydata)

            if t==10:
                F1trace.update(yaxis='y2', legendgroup='group2', showlegend=False)
                F2trace.update(yaxis='y2', legendgroup='group2', showlegend=False)
                F3trace.update(yaxis='y2', legendgroup='group2', showlegend=False)
                F4trace.update(yaxis='y2', legendgroup='group2', showlegend=False)
            fig.add_trace(F1trace)
            fig.add_trace(F2trace)
            fig.add_trace(F3trace)
            fig.add_trace(F4trace)
            #fig.update_layout(title='R={}; D={}; 𝜏={}'.format(r,d,tau))
            #fig['layout']['yaxis'].update(range=[0, y_max])
            #fig['layout']['yaxis2'].update(range=[0, y_max])


        py.plot(fig, include_mathjax='cdn')
        fig.write_image('figs/figRuntimeR{}D{}tau{}.pdf'.format(r,d,tau))
        #fig.write_image('figs/TOMinMaxfigRuntimeR{}D{}tau{}.pdf'.format(r,d,tau))


    def compute_single_tau_plot(self, d, tmax):
        r=self.no_of_robots_list[0] # No of robots
        # Pick the data for this plot only
        row_fields = [' ', ' .1', ' .2']
        for f in self.formulations_list:
            for t in self.no_of_tasks_list:
                row_fields.append('F'+str(f)+'D'+str(d)+'T'+str(t))
        col_fields = ['Avg']
        df = pd.read_csv('aggregatedDataMinAvgMaxR'+str(r)+'.csv', usecols=row_fields, index_col=False)
        print(df[df[' .2'].str.contains(col_fields[0])])
        fig = self.draw_figure()
        y_max = 0
        tasks_reversed = self.no_of_tasks_list[::-1]
        for t in tasks_reversed: 
            F1trace = self.F1_trace()
            ydata = df[df[' .2'].str.contains(col_fields[0])]
            ydata = ydata[ydata[' '].isin(['Tmax'+str(tmax)])]['F'+str(self.formulations_list[0])+'D'+str(d)+'T'+str(t)].tolist()
            ydata_max = max(ydata)
            if ydata_max > y_max:
                y_max = ydata_max
            F1trace.update(x=self.delta_param_list, y=ydata)

            F2trace = self.F2_trace()
            ydata = df[df[' .2'].str.contains(col_fields[0])]
            ydata = ydata[ydata[' '].isin(['Tmax'+str(tmax)])]['F'+str(self.formulations_list[1])+'D'+str(d)+'T'+str(t)].tolist()
            ydata_max = max(ydata)
            if ydata_max > y_max:
                y_max = ydata_max
            F2trace.update(x=self.delta_param_list, y=ydata)

            F3trace = self.F3_trace()
            ydata = df[df[' .2'].str.contains(col_fields[0])]
            ydata = ydata[ydata[' '].isin(['Tmax'+str(tmax)])]['F'+str(self.formulations_list[2])+'D'+str(d)+'T'+str(t)].tolist()
            ydata_max = max(ydata)
            if ydata_max > y_max:
                y_max = ydata_max
            F3trace.update(x=self.delta_param_list, y=ydata)

            F4trace = self.F4_trace()
            ydata = df[df[' .2'].str.contains(col_fields[0])]
            ydata = ydata[ydata[' '].isin(['Tmax'+str(tmax)])]['F'+str(self.formulations_list[3])+'D'+str(d)+'T'+str(t)].tolist()
            ydata_max = max(ydata)
            if ydata_max > y_max:
                y_max = ydata_max
            F4trace.update(x=self.delta_param_list, y=ydata)


            if t==10:
                F1trace.update(yaxis='y2', legendgroup='group2', showlegend=False)
                F2trace.update(yaxis='y2', legendgroup='group2', showlegend=False)
                F3trace.update(yaxis='y2', legendgroup='group2', showlegend=False)
                F4trace.update(yaxis='y2', legendgroup='group2', showlegend=False)
            fig.add_trace(F1trace)
            fig.add_trace(F2trace)
            fig.add_trace(F3trace)
            fig.add_trace(F4trace)
            #fig.update_layout(title='R={}; D={}; 𝓣<sub>max</sub>={}'.format(r,d,tmax))
            fig.update_layout(xaxis=dict(tickvals=self.delta_param_list, title="𝜏 (sec)"))
            #fig['layout']['yaxis'].update(range=[0, y_max])
            #fig['layout']['yaxis2'].update(range=[0, y_max])


        py.plot(fig, include_mathjax='cdn')
        fig.write_image('figs/figRuntimeR{}D{}tmax{}.pdf'.format(r,d,tmax))
        #fig.write_image('figs/TOMinMaxfigRuntimeR{}D{}tmax{}.pdf'.format(r,d,tmax))


    def individual_trace(self):
        # Basic trace to be used to create other traces/lines
        trace = go.Scatter(
            text=[],
            hovertext=[],
            x=[],
            y=[],
            mode='markers+lines',
            legendgroup='group1',
            # hoverinfo='text',
            line=dict(
                color='darkblue',
                width=3
            ),
            name='',
            marker=dict(
                size=6,
                color='blue',
                line=dict(
                    # color='rgba(217, 217, 217, 0.14)',
                    width=0.5
                ),
                opacity=0.8
            )
        )
        return trace

    def F1_trace(self):
        new_trace = self.individual_trace()
        new_trace.name = '𝓕'+str(self.formulations_list[0])
        new_trace.marker.color = 'red'
        new_trace.line.color = 'darkred'
        return new_trace

    def F2_trace(self):
        new_trace = self.individual_trace()
        new_trace.name = '𝓕'+str(self.formulations_list[1])
        new_trace.marker.color = 'blue'
        new_trace.line.color = 'darkblue'
        return new_trace

    def F3_trace(self):
        new_trace = self.individual_trace()
        new_trace.name = '𝓕'+str(self.formulations_list[2])
        new_trace.marker.color = 'green'
        new_trace.line.color = 'darkgreen'
        return new_trace

    def F4_trace(self):
        new_trace = self.individual_trace()
        new_trace.name = '𝓕'+str(self.formulations_list[3])
        new_trace.marker.color = 'violet'
        new_trace.line.color = 'darkviolet'
        return new_trace

    def draw_figure(self):
        data=[]
        layout = go.Layout(
            #width=1100,
            #height=900,
            #autosize=False,
            title='',
            xaxis=dict(tickvals=self.Tmax_param_list, title=),
            yaxis=dict(domain=[0,0.45], range=[-2,3], type="log"),
            yaxis2=dict(domain=[0.55,1], range=[-2,3], type="log"),
            font=dict(size=24),
            #scene=dict(
            #    xaxis_title="𝓣<sub>max</sub>",
            #    yaxis_title="Computation Time",
                #camera=dict(
                #    up=dict(
                #        x=0,
                #        y=0,
                #        z=1
                #    ),
                #    eye=dict(
                #        x=0,
                #        y=1.0707,
                #        z=1,
                #    )
                #),
            #),
            showlegend=True,
        )
        fig = go.Figure(data=data, layout=layout)
        fig.update_layout(
            annotations=[
                go.layout.Annotation(
                    {
                        'showarrow': False,
                        'text': 'Computation Time (sec)',
                        'x': 0,
                        'xshift': -72,
                        'xanchor': 'center',
                        'xref': 'paper',
                        'y': 0.5,
                        'yanchor': 'middle',
                        'yref': 'paper',
                        'yshift': 0.0,
                        'textangle': -90,
                    
                        "font": dict(
                            # family="Courier New, monospace",
                            size=24,
                            # color="#ffffff"
                            ),
                    }
                )
            ]
        )
        return fig




def main():
    formulations_list = [1,2,3,4]
    no_of_robots_list = [4] # We can only put one robot number here.
    no_of_depots_list =[1,2,3]
    no_of_tasks_list = [5, 10]
    delta_param_list = [50, 75, 100, 125, 150]
    Tmax_param_list = [50, 75, 150, 300, 450, 600]
    iterations_list = [i for i in range(10)]

    fig_generator = DataFiguresGenerator(
                        formulations_list,
                        no_of_robots_list,
                        no_of_depots_list,
                        no_of_tasks_list,
                        delta_param_list,
                        Tmax_param_list,
                        iterations_list)

    fig_generator.compute_tau_plots()
    fig_generator.compute_Tmax_plots()

if __name__ == "__main__":
    main()
