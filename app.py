# 1. Import Dash
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import strategy
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd

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
                 "you to compare investing strategies by visualizing the returns from any historic "
                 "stock data you are interested in.", style={'font-size': '12px'}),
])

@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

ticker_view = dbc.Row([
    dbc.Col([
        dbc.Input(type="text", id="ticker-input", value="^GSPC"),
        ], width=6),
    dbc.Col([
        dbc.Label('', id='ticker-check-label')
        ], width=6)
    ], justify='center', align='center')

strategy_options = {'Lump sum': strategy.lump_sum_gain,
                    'DCA': strategy.dca_gain,
                    'Equal stock': strategy.equal_stock_gain}

# style=dict(display='flex', justifyContent='end')
# dbc.Col(html.Img(src='https://upload.wikimedia.org/wikipedia/commons/5/5a/Info_Simple_bw.svg',
#                  style={'height': '10px', 'margin-right': '15px'}), width=3),
strategy_items = dbc.Row([
                dbc.Col(
                dcc.Dropdown(
                    options=[{'label': k, 'value': k} for k in strategy_options],
                    value='Lump sum',
                    clearable=False,
                    id="strategy-input-1"), width=3),
                ' vs ',
                dbc.Col(
                    dcc.Dropdown(
                        options=[{'label': k, 'value': k} for k in strategy_options],
                        value='DCA',
                        clearable=False,
                        id="strategy-input-2"), width=3),

            # dbc.Label("Strategy 2", style={'width': '20%', 'align': 'center'}),
            # html.Img(src='https://upload.wikimedia.org/wikipedia/commons/5/5a/Info_Simple_bw.svg',
            #          style={'height': '10px', 'margin-left': '15px'}),
        ], justify='center')

period = dbc.Col([
    dbc.Label("Investing period"),
    dcc.Dropdown(
        options=[
            {"label": "1 year", "value": 1},
            {"label": "3 years", "value": 3},
            {"label": "5 years", "value": 5},
            {"label": "10 years", "value": 10},
        ],
        value=5,
        id="radioitems-input-3",
        clearable=False,
    )
], width=6)

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

option_view = dbc.Form([explanation_view, ticker_view, html.Br(), range_slider, period, html.Br(), gain])


figures_view = dbc.Row([
    title,
    strategy_items,
    html.Br(),
    html.Br(),
    html.Center(html.Hr(style={'width': '50%'})),
    dbc.Col([
            dcc.Loading(
                children=dcc.Graph(id='timeseries', style={'aspect-ratio': '3/1'}),
            ),
dcc.Loading(children=[
                html.Center([dcc.Graph(id="distribution-scatter",
                                       style={'width': '50%', 'aspect-ratio': '1/1'})]),
                html.Center(dbc.Label("hover here", style={'text-align': 'center'}, html_for='distribution-scatter')),
            ]),

        ], width=5),
        dbc.Col([
            dcc.Loading(children=[
                html.Center(dbc.Label("", id='distribution-1-label', html_for='distribution-1')),
                dcc.Graph(id="distribution-1", style={'aspect-ratio': '3/1'}),
            ]),
            dcc.Loading(children=[
                html.Center(dbc.Label("sometext", style={'text-align': 'center'}, html_for='distribution-1')),
                dbc.Button("Open Offcanvas", id="open-offcanvas", n_clicks=0),
                dbc.Offcanvas(
                    html.P(
                        "This is the content of the Offcanvas. "
                        "Close it by clicking on the close button, or "
                        "the backdrop."
                    ),
                    id="offcanvas",
                    placement='bottom',
                    title="Title",
                    is_open=False,
                ),
                dcc.Graph(id="distribution-2", style={'aspect-ratio': '3/1'}),
            ])
        ], width=5),
    ])


grid = dbc.Row([
    dbc.Col([figures_view], width=7),
    dbc.Col([option_view], width=4),
], align='center', justify='center')

investing = strategy.Investing()


def add_px(fig: go.Figure, px_object):
    fig.add_traces(list(px_object.select_traces()))

@app.callback([Output('ticker-check-label', 'children'),
                Output('timeseries', 'figure'),
               Output('distribution-1', 'figure'),
               Output('distribution-1-label', 'children'),
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

    triggers = dash.callback_context.triggered
    trigger_ids = [trigger['prop_id'].split('.')[0] for trigger in triggers]

    if (len(trigger_ids) == 1) and (trigger_ids[0] == 'distribution-scatter'):
        raise PreventUpdate


    ''' Draw traces of the feature 'value' based one the currently selected stocks '''
    try:
        investing.set_ticker(ticker_text)
    except:
        return '❌ not a valid ticker', dash.no_update, dash.no_update, ' ', dash.no_update, dash.no_update,
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

    def to_percentage(series: pd.Series):
        return series*100 - 100

    distribution_1 = to_percentage(distribution_1[gains_period])
    distribution_2 = to_percentage(distribution_2[gains_period])

    def get_mean_std_text(series: pd.Series):
        mean = np.mean(series.values)
        std = np.std(series.values)
        return f'mean: {mean:.2f}% std: {std: .2f}%'

    distribution_1_text = f'Distribution {gains_period} {get_mean_std_text(distribution_1)}'
    # print(distribution_1_text)

    min_dis_1 = distribution_1.values.min()
    min_dis_2 = distribution_2.values.min()
    max_dis_1 = distribution_1.values.max()
    max_dis_2 = distribution_2.values.max()
    min_x = min(min_dis_1, min_dis_2)
    max_x = max(max_dis_1, max_dis_2)
    range_x = (min_x, max_x)

    # distribution_1 = distribution_1.to_frame()
    def to_plot(series: pd.Series):
        df = pd.DataFrame()
        df['values'] = series
        df['is_gain'] = df['values'] > 0
        return df

    df_plot = to_plot(distribution_1)
    fig_distribution_1 = px.histogram(data_frame=df_plot, x='values', nbins=30,
                                      color='is_gain',
                                      histnorm='percent', range_x=range_x,
                                      color_discrete_sequence=['pink', 'red'])
    fig_distribution_2 = px.histogram(data_frame=distribution_2, x=gains_period, nbins=30,
                                      histnorm='percent', range_x=range_x,
                                      color_discrete_sequence=['blue'])

    fig_distribution_1.update_layout(**fig_layout_kwargs)
    fig_distribution_2.update_layout(**fig_layout_kwargs)


    # distribution scatter

    joined = distribution_1.to_frame().join(distribution_2, lsuffix='_1', rsuffix='_2')
    joined.columns = ['one', 'two']
    joined['better'] = joined['one'] < joined['two']

    range = [min(min_dis_1, min_dis_2), max(max_dis_1, max_dis_2)]
    fig_distribution_scatter = go.Figure(layout_xaxis_range=range,
                                         layout_yaxis_range=range)

    dates = [(start, end) for start, end in joined.index]

    joined['dates'] = dates
    add_px(fig_distribution_scatter, px.scatter(joined, x='one', y='two', custom_data=['dates'],
                                                color='better'))

    fig_distribution_scatter.add_trace(go.Scatter(x=[range[0], range[1]], y=[range[0], range[1]],
                                                  mode='lines', line=dict(width=1)),)


    fig_distribution_scatter.update_layout(**fig_layout_kwargs)

    return ['✔', fig_timeseries,
            fig_distribution_1, distribution_1_text,
            fig_distribution_2,
            fig_distribution_scatter]


app.layout = dbc.Container(grid, fluid=True)


def main():
    # app.run_server()
    app.run_server(
        dev_tools_ui=True, debug=True,
          dev_tools_hot_reload =True, threaded=True)


if __name__ == "__main__":
    main()