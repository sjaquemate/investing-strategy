# https://www.statworx.com/en/content-hub/blog/how-to-build-a-dashboard-in-python-plotly-dash-step-by-step-tutorial/
import dash
from dash import html
import plotly.graph_objects as go
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import numpy as np
import flask

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

def generate_dropdown():
    return html.Div(className='div-for-dropdown',
             children=[
                 dcc.Dropdown(id='stockselector',
                              options={"hi": 'hi', "bye": 'bye'},
                              multi=True,
                              value='bye',
                              style={'backgroundColor': '#1E1E1E'},
                              className='stockselector')
             ],
             style={'color': '#1E1E1E'})

def generate_app_layout():
    return html.Div(children=[
        html.Div(className='row',
                 children=[
                     html.Div(className='four columns div-user-controls', children=[
                         # html.H2('Dash - STOCK PRICES'),
                         # html.P('''Visualising time series with Plotly - Dash'''),
                         # html.P('''Pick one or more stocks from the dropdown below.'''),
                         # generate_dropdown(),
                     ]),
                     html.Div(className='eight columns div-for-charts bg-grey', children=[
                         # dcc.Graph(id='timeseries', config={'displayModeBar': False},
                         #           className='offset-by-one-column', style={'height': '50%'}),
                         # html.H2('Dash - STOCK PRICES'),
                         html.Div(className='twelve columns', style={'height': '50%'},
                                  children=[]),
                         html.Div(children=[
                             html.Div(style={'width': '50%', 'height': '100%',
                                             'background-color': 'white'}, children=[]),
                             html.Div( style={'border': '2px green solid', 'width': '50%',
                                              'height': '100px'}, children=[]),

                             # dcc.Graph(id='something else', config={'displayModeBar': False},
                             #           className='', style={'display': 'inline-block', 'border': '2px green solid', 'margin-top': 0,
                             #         'width': '50%',
                             #                                'vertical-align': 'top'})]),
                             # dcc.Graph(id='something whole new', config={'displayModeBar': False},
                             #           className='', style={'width': '50%',
                             #                                'height': '70%'}),
                        ], className='row')
                     ]),
        ])
    ])

@app.callback(Output('timeseries', 'figure'),
              [Input('stockselector', 'value')])
def update_timeseries(selected_dropdown_value):
    ''' Draw traces of the feature 'value' based one the currently selected stocks '''

    trace = []

    for stock in selected_dropdown_value:
        trace.append(go.Scatter(x=np.arange(100),
                                 y=np.random.random(100),
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))
    # STEP 3
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    # Define Figure
    # STEP 4
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Stock Prices', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [0, 100]},
              ),

              }

    return figure

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
    app.layout = generate_app_layout()
    app.run_server(debug=False)
    # df = px.data.stocks()

if __name__ ==  "__main__":
    main()
