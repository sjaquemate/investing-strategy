# https://www.statworx.com/en/content-hub/blog/how-to-build-a-dashboard-in-python-plotly-dash-step-by-step-tutorial/
import dash
from dash import html
import plotly.graph_objects as go
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import numpy as np
from strategy import Investing
from datetime import datetime


app = dash.Dash(__name__)
server = app.server
investing = Investing()

def generate_dropdown():
    return html.Div(className='div-for-dropdown',
             children=[
                 dcc.Dropdown(id='stockselector',
                              options=[{'label': "Google", 'value': "GOOG"},
                                       {'label': "Apple" , 'value': 'AAPL'},
                              ],
                              value='S&P500',
                              style={'backgroundColor': '#1E1E1E'},
                              className='stockselector')

             ],
             style={'color': '#1E1E1E'})

def generate_rangeslider():
    return dcc.RangeSlider(
        id='period-range-slider',
        min=1900,
        max=2020,
        step=1,
        dots=False,
        value=[2005, 2015],
        pushable=5,
        updatemode='mouseup',
        tooltip={'placement': 'bottom', 'always_visible': True}
    )

strategy_options = {"dca": None, "vca": None, "lump": None}

def generate_checklist():
    return dcc.Checklist(

        value=[None, None]
    )

app.layout = html.Div(children=[
        html.Div(className='row',
                 children=[
                     html.Div(className='four columns div-user-controls', children=[
                         # left
                         html.H2('Investing Strategy Dashboard'),
                         html.P('Select your stock'),
                         generate_dropdown(),
                         generate_rangeslider(),
                         generate_checklist(),
                     ]),
                     html.Div(className='eight columns div-for-charts bg-grey', children=[
                         html.Div(className='twelve columns', style={'height': '50%', 'border': '0px green solid'},
                                  children=[
                            # top
                            dcc.Graph(id='timeseries', config={'displayModeBar': False}, style={'height': '100%'}),
                                  ]),
                         html.Div(children=[
                             # bottom left
                             html.Div(style={'border': '0px green solid'}, className='six columns', children=[
                                dcc.Graph(id='distribution', config={'displayModeBar': False}, style={'height': '100%'})
                             ]),
                             # bottom right
                             html.Div( style={'border': '0px green solid'}, className='six columns', children=[]),
                         ], className='row', style={'height': '50%', 'border': '0px green solid'})

                         # dcc.Graph(id='something else', config={'displayModeBar': False},
                             #           className='', style={'display': 'inline-block', 'border': '2px green solid', 'margin-top': 0,
                             #         'width': '50%',
                             #                                'vertical-align': 'top'})]),
                             # dcc.Graph(id='something whole new', config={'displayModeBar': False},
                             #           className='', style={'width': '50%',
                             #                                'height': '70%'}),
                     ]),
        ])
    ])


@app.callback(
    Output("dropdown", "options"),
    Input("dropdown", "value"),
)
def update_strategy_options(value):
    options = default_options
    if len(value) >= 3:
        options = [
            {
                "label": option["label"],
                "value": option["value"],
                "disabled": option["value"] not in value,
            }
            for option in options
        ]
    return options


@app.callback([Output('timeseries', 'figure'),
              Output('distribution', 'figure')],
              [Input('stockselector', 'value'),
               Input('period-range-slider', 'value')])
def update_timeseries(selected_dropdown_value, period_values):
    ''' Draw traces of the feature 'value' based one the currently selected stocks '''

    investing.set_ticker(selected_dropdown_value)
    investing.set_interval(datetime(1950, 1, 1), datetime(2010, 1, 1))

    timeseries = investing.get_timeseries()
    x = timeseries.index
    y = timeseries.values
    line_timeseries = go.Scatter(x=x, y=y, mode='lines')

    fig_timeseries = {'data': [line_timeseries],
              'layout': go.Layout(
                  colorway=["red"],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  #margin={'b': 15},
                  hovermode='x',
                  # title={'text': 'Stock Prices', 'font': {'color': 'white'}, 'x': 0.5},
                  # sxaxis={'range': [0, 100]},
              )}




    return fig_timeseries, fig_timeseries

# app.layout = html.Div([
#     html.H1(id='H1', children='Styling using html components', style={'textAlign': 'center', \
#                                                                       'marginTop': 40, 'marginBottom': 40}),
#
#     html.Div(
#         [
#             html.Div(
#                 [
#                     html.Label("Developing Status of the Country"),
#                     dcc.Dropdown(
#                         id="status-dropdown",
#                         className="dropdown",
#                     ),
#                 ]
#             ),
#             html.Div(
#                 [
#                     html.Label("Average schooling years grater than"),
#                     dcc.Dropdown(
#                         id="schooling-dropdown",
#                         className="dropdown",
#                     ),
#                 ]
#             ),
#         ],
#         className="row",
#     ),
#
#     html.Div(
#         [
#             html.Div(
#                 dcc.Input(id="input2", type="text", value='GOOG', placeholder="^GSPC", debounce=True)),
#             html.Div(
#                 dcc.Input(id="input3", type="text", value='GOOG', placeholder="^GSPC", debounce=True)),
#         ]
#     ),
#     # generate_dropdown(),
#     # dcc.Markdown(children="""
#     # ### This is some cool markdown text
#     # """),
#     dcc.Graph(id='bar_plot')
# ])


# @app.callback(Output(component_id='bar_plot', component_property='figure'),
#               [Input(component_id='input2', component_property='value')])
# def graph_update(dropdown_value):
#     print(dropdown_value)
#     fig = go.Figure([go.Scatter(x=df['date'], y=df['{}'.format(dropdown_value)], \
#                                 line=dict(color='firebrick', width=4))
#                      ])
#
#     fig.update_layout(title='Stock prices over time',
#                       xaxis_title='Dates',
#                       yaxis_title='Prices'
#                       )
#     return fig


def main():
    app.run_server(debug=False)
    # df = px.data.stocks()

if __name__ ==  "__main__":
    main()
