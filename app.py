from dataclasses import dataclass
from email.policy import default
from typing import Callable
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from components.rangeslider import range_slider
import strategy
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd

Row = dbc.Row
Col = dbc.Col
Div = html.Div
Markdown = dcc.Markdown
Loading = dcc.Loading

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server

range_slider_view = range_slider("period-range-slider", 1990, 2022, 10, 10)

explanation_view = Markdown("There are multiple strategies to invest your money into the stockmarket, "
                 "each having its own trade-off between risk and rewards. This dashboard allows "
                 "you to compare investing strategies by visualizing the returns from any historic "
                 "stock data you are interested in.", style={'font-size': '12px'})

ticker_view = Row([
    Col(dbc.Input(type="text", id="ticker-input", value="^GSPC"), width=6),
    Col(dbc.Label('', id='ticker-check-label'), width=6)
], justify='center', align='center')

@dataclass
class Strategy:
    name: str
    color: str
    function: Callable
    info: str = ''
    
strategies = {
    'Lump sum': Strategy('Lump sum', '#ffa600', strategy.lump_sum_gain, 'expl'),
    'DCA': Strategy('Dollar cost averaging', '#ff6361', strategy.dca_gain, 'expl'),
    'Equal stock': Strategy('Equal stock', '#003f5c', strategy.equal_stock_gain, 'expl')
}

options = [{'label': strategy, 'value': strategy} for strategy in strategies]

def strategy_dropdown(id, options, default_value):
    return dcc.Dropdown(id=id, options=options, value=default_value, clearable=False)
  
def badge_button(text, id):
    return dbc.Badge(text, id=id, style={'cursor': 'pointer'})
    
strategy_items = dbc.Col([
    Row([
        Col( strategy_dropdown("strategy-input-1", options, list(strategies)[0]), width=3 ),
        Col( strategy_dropdown("strategy-input-2", options, list(strategies)[1]), width=3 )
    ], justify='center'),
    
    Row([ 
        Col(Loading(badge_button("info <", id='info-1')), width=2,  align='center'),
        Col(Loading(badge_button("> info", id='info-2')), width=2,  align='center'),
    ], justify='center'),
])

investing_period_view = Col([
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

returns_period_view = Div([
    dbc.Label("Return period"),
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



title = Row(Col(Markdown("### investing strategy dashboard"), 
            style={'text-align': "center", 'margin': 30}, width=10), 
        justify='center')

options_view = dbc.Form([explanation_view, ticker_view, html.Br(), 
                        range_slider_view, investing_period_view, html.Br(), 
                        returns_period_view])

figures_view = Row([
    dbc.Offcanvas(
        Markdown("", id='offcanvas-text'),
        id="offcanvas", placement='bottom', title="", is_open=False,
    ),
    title,
    strategy_items,
    Row(Col(html.Hr(), width=6), justify='center'),
    
    Col([
        Loading(dcc.Graph(id='timeseries', style={'aspect-ratio': '3/1'})),
        html.Br(),
        Loading([
            dcc.Graph(id="distribution-scatter",
                      style={'width': '50%', 'aspect-ratio': '1/1'}),
            dbc.Label("hover here", html_for='distribution-scatter'),
        ]),
    ], width=6),
    
    Col([
        Loading([
            dbc.Label("text", id='distribution-1-label', html_for='distribution-1'),
            dcc.Graph(id="distribution-1", style={'aspect-ratio': '3/1'}),
            dbc.Label("return (%)", html_for='distribution-1')
        ]),
        html.Br(),
        dcc.Loading([
            dbc.Label("", id='distribution-2-label', html_for='distribution-1'),
            dcc.Graph(id="distribution-2", style={'aspect-ratio': '3/1'}),
            dbc.Label("return (%)", html_for='distribution-2'),
        ])
    ], width=6),
])


grid = Row([
    Col(figures_view, width=8),
    Col(options_view, width=3, className='mt-5'),
], justify='center')

investing = strategy.Investing()


def add_px(fig: go.Figure, px_object):
    fig.add_traces(list(px_object.select_traces()))

@app.callback(
    [Output("offcanvas", "is_open"), 
     Output("offcanvas", "title"),
     Output("offcanvas-text", 'children')],
    [Input("info-1", "n_clicks"),
     Input("info-2", "n_clicks")],
    [State("offcanvas", "is_open"),
     State('strategy-input-1', 'value'),
     State('strategy-input-2', 'value')],
)
def toggle_offcanvas(n_clicks_1, n_clicks_2, is_open_prev, strategy_input_1, strategy_input_2):
    
    is_open = dash.no_update    
    if n_clicks_1 or n_clicks_2:
        is_open = not is_open_prev
    
    if n_clicks_1:
        strategy = strategies[strategy_input_1]
    elif n_clicks_2:
        strategy = strategies[strategy_input_2]
    else:    
        raise PreventUpdate
        
    return [is_open, strategy.name, strategy.info] 


@app.callback([Output('ticker-check-label', 'children'),
               Output('timeseries', 'figure'),
               Output('distribution-1', 'figure'),
               Output('distribution-1-label', 'children'),
               Output('distribution-2', 'figure'),
               Output('distribution-2-label', 'children'),
               Output('distribution-scatter', 'figure'),
               Output("info-1", 'color'),
               Output("info-2", 'color'),
               ],
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
        return ['❌ not a valid ticker'] + [dash.no_update]*8
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


    add_px(fig_timeseries, px.area(timeseries_selected, color_discrete_sequence=['yellow']))

    if scatter_hoverdata is not None:

        start_date, end_date = scatter_hoverdata['points'][0]['customdata'][0]
        # start_date, end_date = investing.get_interval_dates()
        is_selected = (start_date <= timeseries.index) & (timeseries.index <= end_date)
        timeseries_selected = timeseries[is_selected]

        add_px(fig_timeseries, px.area(timeseries_selected,
                                       color_discrete_sequence=['purple']))

    add_px(fig_timeseries, px.line(timeseries, color_discrete_sequence=['red']))

    fig_timeseries.update_layout(**fig_layout_kwargs)

    # distribution
    print(strategy_input_1)
    
    strategy_1 = strategies[strategy_input_1]
    strategy_2 = strategies[strategy_input_2]

    distribution_1 = investing.calculate_distribution(strategy_1.function, investing_duration_years)
    distribution_2 = investing.calculate_distribution(strategy_2.function, investing_duration_years)

    def to_percentage(series: pd.Series):
        return series*100 - 100

    distribution_1 = to_percentage(distribution_1[gains_period])
    distribution_2 = to_percentage(distribution_2[gains_period])

    def get_mean_std_text(series: pd.Series):
        mean = np.mean(series.values)
        std = np.std(series.values)
        return f'mean: {mean:.1f}% std: {std:.1f}%'

    distribution_1_text = f'{get_mean_std_text(distribution_1)}'
    distribution_2_text = f'{get_mean_std_text(distribution_2)}'

    # print(distribution_1_text)

    min_dis_1 = distribution_1.values.min()
    min_dis_2 = distribution_2.values.min()
    max_dis_1 = distribution_1.values.max()
    max_dis_2 = distribution_2.values.max()
    min_x = min(min_dis_1, min_dis_2)
    max_x = max(max_dis_1, max_dis_2)
    lim_x = (min_x, max_x)
    range_x = np.linspace(min_x, max_x, 5)
    
    def to_plot(series: pd.Series):
        df = pd.DataFrame()
        df['values'] = series
        df['is_gain'] = df['values'] > 0
        return df

    df_plot = to_plot(distribution_1)
    fig_distribution_1 = px.histogram(data_frame=df_plot, x='values', nbins=30,
                                      color='is_gain',
                                      histnorm='percent', range_x=lim_x,
                                      color_discrete_sequence=[strategy_1.color, 'black'])
    fig_distribution_2 = px.histogram(data_frame=distribution_2, x=gains_period, nbins=30,
                                      histnorm='percent', range_x=lim_x,
                                      color_discrete_sequence=[strategy_2.color])

    fig_distribution_1.update_layout(
        **fig_layout_kwargs,
        xaxis_title="",
        yaxis_title="",
    )
    fig_distribution_2.update_layout(
        **fig_layout_kwargs,
        xaxis_title="",
        yaxis_title=""
    )

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
                                                color='better', 
                                                color_discrete_sequence=[strategy_1.color, strategy_2.color]))

    fig_distribution_scatter.add_trace(go.Scatter(x=[range[0], range[1]], y=[range[0], range[1]],
                                                  mode='lines', line=dict(width=1)))


    fig_distribution_scatter.update_layout(**fig_layout_kwargs)
    
    return ['✔', fig_timeseries,
            fig_distribution_1, distribution_1_text,
            fig_distribution_2, distribution_2_text,
            fig_distribution_scatter,
            strategy_1.color,
            strategy_2.color,
            ]


app.layout = dbc.Container(grid, fluid=True)


def main():
    app.run_server(
        dev_tools_ui=True, debug=True,
          dev_tools_hot_reload =True, threaded=True)


if __name__ == "__main__":
    main()