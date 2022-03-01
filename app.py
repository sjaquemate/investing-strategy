# 1. Import Dash
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import strategy

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server

range_slider = dbc.Col(
    [
        # dbc.Label("RangeSlider", html_for="period-range-slider"),
        dcc.RangeSlider(id="period-range-slider",
                        min=1990, max=2022, value=[1990, 2022],
                        marks={year: str(year) for year in range(1990, 2022, 10)},
                        step=1, dots=False,
                        pushable=10, updatemode='mouseup',
                        tooltip={'placement': 'top', 'always_visible': True}
                        ),
    ]
)

explanation_view = html.Div([
    dcc.Markdown("There are multiple strategies to invest your money into the stockmarket, "
                 "each having its own trade-off between risk and rewards. This dashboard allows "
                 "you to compare investing strategies by visualizing the returns from historic "
                 "stock data"),
])

ticker_view = html.Div([
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
                label_checked_style={"color": "red"},
                input_checked_style={
                    "backgroundColor": "red",
                    "borderColor": "red",
                },
            )
        ]),
        dbc.Col([
            dbc.Label("Strategy 2"),
            dbc.RadioItems(
                options=[{'label': k, 'value': k} for k in strategy_options],
                value='DCA',
                id="strategy-input-2",
                label_checked_style={"color": "blue"},
                input_checked_style={
                    "backgroundColor": "blue",
                    "borderColor": "blue",
                },
            )
        ])
    ]
)

period = html.Div([
    dbc.Label("Investing period"),
    dbc.RadioItems(
        options=[
            {"label": "1 year", "value": 1},
            {"label": "3 years", "value": 3},
            {"label": "5 years", "value": 5},
            {"label": "10 years", "value": 10},
        ],
        value=1,
        id="radioitems-input-3",
        inline=True,
    )
])
gain = html.Div([
    dbc.RadioItems(
        options=[
            {"label": "yearly return", "value": 'gains_yearly'},
            {"label": "total return", "value": 'gains_total'},
        ],
        value='gains_yearly',
        id="radioitems-input-4",
        inline=True,
    )
])

title = dbc.Row(dcc.Markdown("### investing strategy dashboard"), style={'text-align': "center",
                                                                         'margin': 30})

option_view = dbc.Form([explanation_view, ticker_view, range_slider, strategy_items, period, gain])

figures_view = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='timeseries', style={'aspect-ratio': '3/1'}),
            html.Center([dcc.Graph(id="distribution-scatter",
                      style={'width': '50%', 'aspect-ratio': '1/1'})]),
            html.Center(dbc.Label("hover here", style={'text-align': 'center'}, html_for='distribution-scatter')),
        ], width=6),
        dbc.Col([
            html.Center(dbc.Label("Distribution of returns",  html_for='distribution-1')),
            dcc.Graph(id="distribution-1", style={'aspect-ratio': '3/1'}),
            html.Center(dbc.Label("sometext", style={'text-align': 'center'}, html_for='distribution-1')),
            dcc.Graph(id="distribution-2", style={'aspect-ratio': '3/1'}),
        ], width=6),
    ])
])


grid = dbc.Row([title,
    dbc.Col([option_view], width=3),
    dbc.Col([figures_view], width=9),
])

investing = strategy.Investing()


def add_px(fig: go.Figure, px_object):
    fig.add_traces(list(px_object.select_traces()))

# todo create timeseries overlay figure

@app.callback([Output('timeseries', 'figure'),
               Output('distribution-1', 'figure'),
               Output('distribution-2', 'figure'),
               Output('distribution-scatter', 'figure')],
              [Input('ticker-input', 'value'),
               Input('period-range-slider', 'value'),
               Input('strategy-input-1', 'value'),
               Input('strategy-input-2', 'value'),
               Input('radioitems-input-3', 'value'),
               Input('radioitems-input-4', 'value'),
               Input('distribution-scatter', 'hoverData')])

def update_graphs(ticker_text, year_interval, strategy_input_1, strategy_input_2,
                  investing_duration_years, gains_period,
                  scatter_hoverdata):
    if False:
        return dash.no_update
    ''' Draw traces of the feature 'value' based one the currently selected stocks '''
    investing.set_ticker(ticker_text)
    # todo if not valid set error message

    start_year, end_year = year_interval
    investing.set_interval_years(start_year, end_year)

    fig_layout_kwargs = {'margin': dict(l=0, r=0, t=0, b=0),
                         'plot_bgcolor': 'rgb(0, 0, 0, 0)',
                         'paper_bgcolor': 'rgb(0, 0, 0, 0)',
                         'showlegend': False,
                         # 'hovermode': 'x',
                         }

    # timeseries
    fig_timeseries = go.Figure()


    timeseries = investing.get_timeseries().to_frame()
    start_date, end_date = investing.get_interval_dates()
    is_selected = (start_date <= timeseries.index) & (timeseries.index <= end_date)
    timeseries_selected = timeseries[is_selected]


    add_px(fig_timeseries, px.area(timeseries_selected, color_discrete_sequence=['rgba(0, 0, 0, 0.5)']))

    if scatter_hoverdata is not None:

        start_date, end_date = scatter_hoverdata['points'][0]['customdata'][0]
        # start_date, end_date = investing.get_interval_dates()
        is_selected = (start_date <= timeseries.index) & (timeseries.index <= end_date)
        timeseries_selected = timeseries[is_selected]

        add_px(fig_timeseries, px.area(timeseries_selected,
                                       color_discrete_sequence=['purple']))

    add_px(fig_timeseries, px.line(timeseries, color_discrete_sequence=['blue']))

    fig_timeseries.update_layout(**fig_layout_kwargs)

    # distribution
    strategy_1 = strategy_options[strategy_input_1]
    strategy_2 = strategy_options[strategy_input_2]

    distribution_1 = investing.calculate_distribution(strategy_1, investing_duration_years)
    distribution_2 = investing.calculate_distribution(strategy_2, investing_duration_years)

    distribution_1 = distribution_1[[gains_period]]
    distribution_2 = distribution_2[[gains_period]]

    min_dis_1 = distribution_1.values.min()
    min_dis_2 = distribution_2.values.min()
    max_dis_1 = distribution_1.values.max()
    max_dis_2 = distribution_2.values.max()
    min_x = min(min_dis_1, min_dis_2)
    max_x = max(max_dis_1, max_dis_2)
    range_x = (min_x, max_x)

    fig_distribution_1 = px.histogram(data_frame=distribution_1, x=gains_period, nbins=30,
                                      histnorm='percent', range_x=range_x,
                                      color_discrete_sequence=['red'])
    fig_distribution_2 = px.histogram(data_frame=distribution_2, x=gains_period, nbins=30,
                                      histnorm='percent', range_x=range_x,
                                      color_discrete_sequence=['blue'])

    fig_distribution_1.update_layout(**fig_layout_kwargs)
    fig_distribution_2.update_layout(**fig_layout_kwargs)


    # distribution scatter

    distribution_1.columns = ['one']
    distribution_2.columns = ['two']
    joined = distribution_1.join(distribution_2)
    joined['better'] = joined['one'] < joined['two']

    range = [min(min_dis_1, min_dis_2), max(max_dis_1, max_dis_2)]
    fig_distribution_scatter = go.Figure(layout_xaxis_range=range,
                                         layout_yaxis_range=range)

    dates = [(start, end) for start, end in joined.index]

    joined['dates'] = dates
    add_px(fig_distribution_scatter, px.scatter(joined, x='one', y='two', custom_data=['dates'],
                                                color='better'))

    fig_distribution_scatter.add_trace(go.Scatter(x=[range[0], range[1]], y=[range[0], range[1]],
                                                  mode='lines', line=dict(width=1)))

    # fig_distribution_scatter.add_trace(go.Scatter(x=[range[0], 1, 1], y=[range[0], 1, range[0]],
    #                                               fill='toself', fillcolor='rgba(1, 255, 1, .1)',
    #                                               mode='lines', line=dict(width=0)))
    # fig_distribution_scatter.add_trace(go.Scatter(x=[1, range[1], range[1]], y=[1, range[1], 1],
    #                                               fill='toself', fillcolor='rgba(1, 1, 255, .1)',
    #                                               mode='lines', line=dict(width=0)))
    # fig_distribution_scatter.add_trace(go.Scatter(x=[range[0], range[0], 1], y=[range[0], 1, 1],
    #                                               fill='toself', fillcolor='rgba(255, 1, 0, .1)',
    #                                               mode='lines', line=dict(width=0)))
    # fig_distribution_scatter.add_trace(go.Scatter(x=[1, 1, range[1]], y=[1, range[1], range[1]],
    #                                               fill='toself', fillcolor='rgba(209, 50, 255, .1)',
    #                                               mode='lines', line=dict(width=0)))

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
    app.run_server()
    # app.run_server(
    #     dev_tools_ui=True, debug=True,
    #       dev_tools_hot_reload =True, threaded=True)


if __name__ == "__main__":
    main()