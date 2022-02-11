# 1. Import Dash
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import strategy

app = dash.Dash(external_stylesheets=[dbc.themes.SIMPLEX])

range_slider = dbc.Col(
    [
        dbc.Label("RangeSlider", html_for="period-range-slider"),
        dcc.RangeSlider(id="period-range-slider",
                        min=1990, max=2022, value=[1990, 2022],
                        marks={year: str(year) for year in range(1990, 2022, 10)},
                        step=1, dots=False,
                        pushable=5, updatemode='mouseup',
                        tooltip={'placement': 'top', 'always_visible': True}
        ),
    ]
)

ticker_view = html.Div([
    dbc.Label("Ticker", html_for="ticker-input"),
    dbc.Input(type="text", id="ticker-input", value="^GSPC"),
    dbc.FormText('E.g: "GOOG", "^gspc", "VUSA.AS"'),
])

strategy_options = {'Lump sum': strategy.lump_sum_gain,
                    'DCA': strategy.dca_gain}

strategy_items = dbc.Row(
    [
    dbc.Col([
        dbc.Label("Strategy 1"),
        dbc.RadioItems(
            options=[{'label': k, 'value': k} for k in strategy_options],
            value='Lump sum',
            id="strategy-input-1",
        )
    ]),
    dbc.Col([
        dbc.Label("Strategy 2"),
        dbc.RadioItems(
            options=[{'label': k, 'value': k} for k in strategy_options],
            value='DCA',
            id="strategy-input-2",
        )
    ])
]
)

period = html.Div([
    dbc.Label("Period"),
    dbc.RadioItems(
        options=[
            {"label": "Option 1", "value": 1},
            {"label": "Option 2", "value": 2},
            {"label": "Disabled Option", "value": 3, "disabled": True},
        ],
        value=1,
        id="radioitems-input-3",
    )
])

title = dbc.Row(html.H1("Title"), style={'text-align': "center"})

option_view = dbc.Form([title, ticker_view, range_slider, strategy_items, period])


figures_view = html.Div([
    dbc.Row(html.H1("Figures"), style={'text-align': "center"}),
    dcc.Graph(id='timeseries', style={'aspect-ratio': '4/1'}),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="distribution-1", style={'aspect-ratio': '3/1'}),
            dcc.Graph(id="distribution-2", style={'aspect-ratio': '3/1'}),
        ], width=6),
        dbc.Col([
            dcc.Graph(id="distribution-scatter", style={'aspect-ratio': '1/1'}),
        ], width=6)
    ])
])


grid = dbc.Row([
    dbc.Col(
        option_view, width={'size': 4},
    ),
    dbc.Col(
        figures_view, width={'size': 8, 'order': 'last'}
    ),
])

investing = strategy.Investing()


@app.callback([Output('timeseries', 'figure'),
               Output('distribution-1', 'figure'),
               Output('distribution-2', 'figure'),
               Output('distribution-scatter', 'figure')],
              [Input('ticker-input', 'value'),
               Input('period-range-slider', 'value'),
               Input('strategy-input-1', 'value'),
               Input('strategy-input-2', 'value')])
def update_graphs(ticker_text, year_interval, strategy_input_1, strategy_input_2):
    ''' Draw traces of the feature 'value' based one the currently selected stocks '''

    investing.set_ticker(ticker_text)
    # todo if not valid set error message

    start_year, end_year = year_interval
    investing.set_interval_years(start_year, end_year)


    fig_layout_kwargs = {'margin': dict(l=0, r=0, t=0, b=0),
                         'plot_bgcolor': 'rgb(0, 0, 0, 0)',
                         'paper_bgcolor': 'rgb(0, 0, 0, 0)',
                         'showlegend': False,
                         #'hovermode': 'x',
                         }

    # timeseries
    timeseries = investing.get_timeseries().to_frame()
    start_date, end_date = investing.get_interval_dates()
    is_selected = (start_date <= timeseries.index) & (timeseries.index <= end_date)
    timeseries_selected = timeseries[is_selected]

    line_1 = px.area(timeseries_selected, color_discrete_map={None: 'red'})
    line_2 = px.line(timeseries, color_discrete_map={None: 'blue'})

    fig_timeseries = go.Figure()
    fig_timeseries.add_traces(list(line_2.select_traces()))
    fig_timeseries.add_traces(list(line_1.select_traces()))
    fig_timeseries.update_layout(**fig_layout_kwargs)

    # distribution
    strategy_1 = strategy_options[strategy_input_1]
    strategy_2 = strategy_options[strategy_input_2]

    distribution_1 = investing.calculate_distribution(strategy_1)
    distribution_2 = investing.calculate_distribution(strategy_2)
    min_dis_1 = distribution_1.values.min()
    min_dis_2 = distribution_2.values.min()
    max_dis_1 = distribution_1.values.max()
    max_dis_2 = distribution_2.values.max()
    min_x = min(min_dis_1, min_dis_2)
    max_x = max(max_dis_1, max_dis_2)
    range_x = (min_x, max_x)

    fig_distribution_1 = px.histogram(data_frame=distribution_1, x="gain", nbins=30,
                                        histnorm='percent', range_x=range_x)
    fig_distribution_2 = px.histogram(data_frame=distribution_2, x="gain", nbins=30,
                                      histnorm='percent', range_x=range_x)

    fig_distribution_1.update_layout(**fig_layout_kwargs)
    fig_distribution_2.update_layout(**fig_layout_kwargs)

    def add_px(fig: go.Figure, px_object):
        fig.add_traces(list(px_object.select_traces()))

    # distribution scatter
    distribution_1.columns = ['one']
    distribution_2.columns = ['two']
    joined = distribution_1.join(distribution_2)
    fig_distribution_scatter = go.Figure(layout_xaxis_range=[min_dis_1, max_dis_1],
                                         layout_yaxis_range=[min_dis_2, max_dis_2])

    add_px(fig_distribution_scatter, px.scatter(joined, x='one', y='two'))
    fig_distribution_scatter.add_trace(go.Scatter(x=[min_dis_1, 1], y=[min_dis_2, 1], fill='tozeroy'))
    # p = px.area(x=[0.9, 1], y=[0.9, 1])
    # p.update_layout(**{'fill': 'tonexty'})
    # add_px(fig_distribution_scatter, p)

    # import pandas as pd
    # fig_distribution_scatter.add_scatter(
    #     go.Scatter(x=[min_dis_1, max_dis_1], y=[min_dis_2, max_dis_2])
    # )
    # print(min_dis_1, 1, min_dis_2, 1)
    # fig_distribution_scatter.add_scatter(
    #     go.Scatter(x=[min_dis_1, 1], y=[min_dis_2, 1])
    # )
    fig_distribution_scatter.update_layout(**fig_layout_kwargs)

    return [fig_timeseries, fig_distribution_1, fig_distribution_2, fig_distribution_scatter]


app.layout = dbc.Container(grid, fluid=True)

def main():
    app.run_server()  # (debug=True, threaded=True)

if __name__ == "__main__":
    main()