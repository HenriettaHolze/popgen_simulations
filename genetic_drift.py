#!/usr/bin/env python

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import plotly.express as px

import numpy as np
import pandas as pd

# https://github.com/kholsinger/PopGen-Shiny/blob/master/Genetic-Drift/app.R

#########################
# Dashboard Layout / View
#########################

# Set up Dashboard and create layout
app = dash.Dash(
    __name__  # , external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)
# app = dash.Dash(__name__)

server = app.server

# app.config["suppress_callback_exceptions"] = True


app.layout = html.Div(
    [
        # Page header
        html.Div([html.H1("Allele frequency changes with genetic drift")]),
        # div for sliders and graph
        html.Div(
            [
                # div for sliders
                html.Div(
                    [
                        html.Label("Initial Frequency of A"),
                        dcc.Slider(
                            id="init-p",
                            min=0,
                            max=1,
                            step=0.1,
                            value=0.5,
                            tooltip={"always_visible": True},
                            marks={"0": "0", "1": "1"},
                        ),
                        html.Label("Population size"),
                        dcc.Slider(
                            id="init-N",
                            min=0,
                            max=1000,
                            step=1,
                            value=100,
                            tooltip={"always_visible": True},
                            marks={"0": "0", "1000": "1000"},
                        ),
                        html.Label("Number of generations"),
                        dcc.Slider(
                            id="init-n-gen",
                            min=0,
                            max=1000,
                            step=1,
                            value=100,
                            tooltip={"always_visible": True},
                            marks={"0": "0", "1000": "1000"},
                        ),
                        html.Label("Number of populations"),
                        dcc.Slider(
                            id="init-n-pop",
                            min=0,
                            max=10,
                            step=1,
                            value=5,
                            tooltip={"always_visible": True},
                            marks={"0": "0", "10": "10"},
                        ),
                    ],
                    className="four columns",
                ),
                html.Div(
                    [
                        # html.Label('Plot'),
                        html.Div(id="plot"),
                        # html.Div(id='plot-no-animation-container')
                    ],
                    className="eight columns",
                ),
            ]
        ),
    ]
)


#############################################
# Interaction Between Components / Controller
#############################################


def one_gen(p, N):
    k = np.random.binomial(n=N, p=p, size=1)[0]
    return k / N


def drift(p0, N, n_gen):
    p = [p0]
    for i in range(n_gen):
        p.append(one_gen(p=p[i], N=N))

    return p


@app.callback(
    Output("plot", "children"),
    [
        Input("init-p", "value"),
        Input("init-N", "value"),
        Input("init-n-gen", "value"),
        Input("init-n-pop", "value"),
    ],
)
def update_plot(init_p, init_N, init_n_gen, init_n_pop):

    # make dataframe
    p = []
    for i in range(init_n_pop):
        p.extend(drift(p0=init_p, N=init_N, n_gen=init_n_gen))
    t = list(range(init_n_gen + 1)) * init_n_pop
    pop = [i for i in range(init_n_pop) for b in range(init_n_gen + 1)]
    df = pd.DataFrame({"p": p, "t": t, "pop": pop})

    # make initial frame (first data point for all populations)
    initial_data = []
    for population in range(init_n_pop):
        y_axis = [df.loc[df["pop"] == population, "p"].iloc[0]]
        initial_data.append(
            go.Scatter(x=[0], y=y_axis, mode="lines", name="pop{}".format(population))
        )

    # make all other frames for animation
    numOfFrames = init_n_gen + 1
    frames = []
    for f in range(1, numOfFrames + 1):
        x_axis = np.arange(0, f)
        curr_data = []
        frame_data = df.loc[df["t"] <= f]
        for population in range(init_n_pop):
            y_axis = frame_data.loc[frame_data["pop"] == population, "p"]
            curr_data.append(
                go.Scatter(
                    x=x_axis, y=y_axis, mode="lines", name="pop{}".format(population)
                )
            )
        curr_frame = go.Frame(data=curr_data)
        frames.append(curr_frame)

    fig = go.Figure(
        data=initial_data,
        layout={
            "xaxis": {"range": [0, init_n_gen]},
            "yaxis": {"range": [-0.05, 1.05]},
        },
        frames=frames,
    )

    # Edit the layout
    fig.update_layout(
        #   title='Allele frequency changes with genetic drift',
        xaxis_title="t",
        yaxis_title="p",
        margin=dict(t=30),
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        # speed
                        args=[
                            None,
                            {
                                "frame": {
                                    "duration": 200 / init_n_gen,
                                    "redraw": False,
                                },
                                "fromcurrent": True,
                                "transition": 50 / init_n_gen / 5,
                            },
                        ],
                    ),
                    {
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                        "label": "Pause",
                        "method": "animate",
                    },
                ],
            )
        ],
    )

    return dcc.Graph(id="final_plot", figure=fig)


# @app.callback(
#     Output("plot-no-animation-container", "children"),
#     [
#         Input("init-p", "value"),
#         Input("init-N", "value"),
#         Input("init-n-gen", "value"),
#         Input("init-n-pop", "value"),
#     ],
# )
# def update_plot(init_p, init_N, init_n_gen, init_n_pop):
#     # np.random.seed(1)

#     fig = go.Figure()

#     for i in range(init_n_pop):
#         p = drift(p0=init_p, N=init_N, n_gen=init_n_gen)
#         print(p)

#         fig.add_trace(
#             go.Scatter(x=list(range(init_n_gen + 1)), y=p, name="pop{}".format(i))
#         )

#     # Edit the layout
#     fig.update_layout(
#         title="Allele frequency changes with genetic drift",
#         xaxis_title="t",
#         yaxis_title="p",
#     )

#     return dcc.Graph(id="plot-no-animation", figure=fig)


if __name__ == "__main__":
    # app.run_server(host="127.0.0.1", port=8050, debug=True)
    app.run_server(debug=True)

