from dataclasses import dataclass
from email.policy import default
from typing import Callable
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from components.option_views import rangeslider, dropdown, badgebutton
import strategy
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd
import figures 
from functools import partial

Row = dbc.Row
Col = dbc.Col
Div = html.Div
Markdown = dcc.Markdown
Loading = partial(dcc.Loading, type='dot')
Graph = partial(dcc.Graph, config={'displayModeBar': False})

label_ticker_id = 'label-ticker'
fig_timeseries_id = 'fig-timeseries'
fig_distribution_1_id = 'fig-distribution-1'
label_distribution_1_id = 'label-distribution-1'
fig_distribution_2_id = 'fig-distribution-2'
label_distribution_2_id = 'label-distribution-2'
fig_distribution_scatter_id = 'fig-distribution-scatter'
badge_info_1_id = 'info-1'
badge_info_2_id = 'info-2'

offcanvas_id = 'offcanvas'
offcanvas_text_id = 'offcanvas-text'
input_ticker_id = 'input-ticker'
rangeslider_period_id = 'rangeslider'
input_strategy_1_id = 'input-strategy-1'
input_strategy_2_id = 'input-strategy-2'
input_investing_period_id = 'input-investing-period'
radio_returns_period_id = 'radio-returns-period'

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server

range_slider_view = rangeslider( rangeslider_period_id, 1990, 2022, 10, 10 )

explanation_view = Markdown("There are multiple strategies to invest your money into the stockmarket, "
                 "each having its own trade-off between risk and rewards. This dashboard allows "
                 "you to compare investing strategies by visualizing the returns from any historic "
                 "stock data you are interested in.", style={'font-size': '12px'})

ticker_view = Row([
    Col(dbc.Input(type="text", id=input_ticker_id, value="^GSPC"), width=6),
    Col(dbc.Label('', id=label_ticker_id), width=6)
], justify='center', align='center')

@dataclass
class Strategy:
    name: str
    color: str
    function: Callable
    info: str = ''
    
strategies = {
    'Lump sum': Strategy('Lump sum', '#003f5c', strategy.lump_sum_gain, 'expl'),
    'DCA': Strategy('Dollar cost averaging', '#ff6361', strategy.dca_gain, 'expl'),
    'Equal stock': Strategy('Equal stock', '#ffa600', strategy.equal_stock_gain, 'expl')
}

options = [{'label': strategy, 'value': strategy} for strategy in strategies]

strategy_items = dbc.Col([
    Row([
        Col( Row(badgebutton("info <", id='info-1'), justify='center'), width=2, align='center'),
        Col( dropdown("input-strategy-1", options, list(strategies)[0]), width=3 ),
        Col( dropdown("input-strategy-2", options, list(strategies)[1]), width=3 ),
        Col( Row(badgebutton("> info", id='info-2'), justify='center'), width=2, align='center'),
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
        id=input_investing_period_id,
        clearable=False,
    )
], width=6)

returns_period_view = Div([
    dbc.Label("Return period"),
    dbc.RadioItems(
        options=[
            {"label": "yearly return", "value": 'yearly'},
            {"label": "total return", "value": 'total'},
        ],
        value='yearly',
        id=radio_returns_period_id,
        inline=True,
    )
])

options_view = dbc.Form([explanation_view, ticker_view, html.Br(), 
                         range_slider_view, investing_period_view, html.Br(), 
                         returns_period_view])


title = Row(Col(Markdown("### investing strategy dashboard"), 
                style={'text-align': "center", 'margin': 30}, 
            width=10), 
        justify='center')

figures_view = Row([
    
    dbc.Offcanvas(
        Markdown("", id=offcanvas_text_id),
        id=offcanvas_id, placement='bottom', title="", is_open=False,
    ),
    title,
    strategy_items,
    Row(Col(html.Hr(), width=6), justify='center'),
    
    Col([
        Graph(id=fig_timeseries_id, style={'aspect-ratio': '3/1'}),
        html.Br(),
        Graph(id=fig_distribution_scatter_id,
                    style={'width': '50%', 'aspect-ratio': '1/1'}),
        dbc.Label("hover here", html_for=fig_distribution_scatter_id),
    ], width=6),
    
    Col([
        html.Center(dbc.Label("text", id=label_distribution_1_id, html_for=fig_distribution_1_id)),
        Graph(id=fig_distribution_1_id, style={'aspect-ratio': '3/1'}),
        html.Br(),
        html.Center(dbc.Label("", id=label_distribution_2_id, html_for=fig_distribution_2_id)),
        Graph(id=fig_distribution_2_id, style={'aspect-ratio': '3/1'}),
    ], width=6),
])

grid = Row([
    Col(figures_view, width=8),
    Col(options_view, width=3, className='mt-5'),
], justify='center')

investing = strategy.Investing()

def calc_mean_std(series: pd.Series):
    mean = np.mean(series.values)
    std = np.std(series.values)
    return mean, std
    
@app.callback(
    [Output(offcanvas_id, "is_open"), 
     Output(offcanvas_id, "title"),
     Output(offcanvas_text_id, 'children')],
    [Input(badge_info_1_id, "n_clicks"),
     Input(badge_info_2_id, "n_clicks")],
    [State(offcanvas_id, "is_open"),
     State(input_strategy_1_id, 'value'),
     State(input_strategy_2_id, 'value')],
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

@app.callback([Output(label_ticker_id, 'children'),
               Output(fig_timeseries_id, 'figure'),
               Output(fig_distribution_1_id, 'figure'),
               Output(label_distribution_1_id, 'children'),
               Output(fig_distribution_2_id, 'figure'),
               Output(label_distribution_2_id, 'children'),
               Output(fig_distribution_scatter_id, 'figure'),
               Output(badge_info_1_id, 'color'),
               Output(badge_info_2_id, 'color')],
              [Input(input_ticker_id, 'value'),
               Input(rangeslider_period_id, 'value'),
               Input(input_strategy_1_id, 'value'),
               Input(input_strategy_2_id, 'value'),
               Input(input_investing_period_id, 'value'),
               Input(radio_returns_period_id, 'value'),
               Input(fig_distribution_scatter_id, 'hoverData')])
def update_graphs(ticker_text, year_interval, 
                  strategy_input_1, strategy_input_2,
                  investing_period, returns_period,
                  scatter_hoverdata):

    triggers = dash.callback_context.triggered
    trigger_ids = [trigger['prop_id'].split('.')[0] for trigger in triggers]

    if (len(trigger_ids) == 1) and (trigger_ids[0] == 'distribution-scatter'):
        raise PreventUpdate

    try:
        investing.set_ticker(ticker_text)
    except:
        return ['❌ not a valid ticker'] + [dash.no_update]*8

    start_year, end_year = year_interval
    investing.set_interval_years(start_year, end_year)

    ### timeseries ###
    timeseries = investing.get_timeseries()
    start_date, end_date = investing.get_interval_dates()
    fig_timeseries = figures.make_timeseries_figure(timeseries, start_date, end_date,
                                                    linecolor='black', highlightcolor='black')
    
    ### distribution histograms ###
    strategy_1 = strategies[strategy_input_1]
    strategy_2 = strategies[strategy_input_2]

    yearly = returns_period == 'yearly'
    
    distribution_1 = investing.calculate_distribution(strategy_1.function, investing_period, 
                                                      as_percentage=True, yearly=yearly)

    distribution_2 = investing.calculate_distribution(strategy_2.function, investing_period, 
                                                      as_percentage=True, yearly=yearly)

    generate_distribution_text = lambda mean, std: f'mean: {mean:.1f}% std: {std:.1f}%'
    distribution_1_text = generate_distribution_text(*calc_mean_std(distribution_1))
    distribution_2_text = generate_distribution_text(*calc_mean_std(distribution_2))

    min_x = min(min(distribution_1), min(distribution_2))
    max_x = max(max(distribution_1), max(distribution_2))
    
    fig_distribution_1 = figures.make_distribution_histogram_figure(distribution_1, (min_x, max_x), strategy_1.color)
    fig_distribution_2 = figures.make_distribution_histogram_figure(distribution_2, (min_x, max_x), strategy_2.color)
    
    ### distribution scatter ###
    fig_distribution_scatter = figures.make_distribution_scatter_figure(distribution_1, distribution_2,
                                                                        strategy_1.color, strategy_2.color)
    
    return [
        '✔', 
        fig_timeseries,
        fig_distribution_1, 
        distribution_1_text,
        fig_distribution_2, 
        distribution_2_text,
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