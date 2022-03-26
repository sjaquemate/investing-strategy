from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd 
import numpy as np 
from functools import lru_cache


fig_layout_kwargs = {
    'margin': dict(l=0, r=0, t=0, b=0),
    'plot_bgcolor': 'rgb(0, 0, 0, 0)',
    'paper_bgcolor': 'rgb(0, 0, 0, 0)',
    'showlegend': False,
    'hovermode': 'x',
}

def add_px(fig: go.Figure, px_object):
    fig.add_traces(list(px_object.select_traces()))
    
def make_timeseries_figure(timeseries: pd.Series, 
                           highlight_start_date: datetime, highlight_end_date: datetime,
                           linecolor: str, highlightcolor: str) -> go.Figure:
    fig = go.Figure()

    is_highlighted = (highlight_start_date <= timeseries.index) & \
                     (timeseries.index <= highlight_end_date)
    timeseries_highlighted = timeseries[is_highlighted]

    add_px(fig, px.area(timeseries_highlighted, color_discrete_sequence=[highlightcolor]))
    add_px(fig, px.line(timeseries, color_discrete_sequence=[linecolor]))

    # if scatter_hoverdata is not None:

    #     start_date, end_date = scatter_hoverdata['points'][0]['customdata'][0]
    #     # start_date, end_date = investing.get_interval_dates()
    #     is_selected = (start_date <= timeseries.index) & (timeseries.index <= end_date)
    #     timeseries_selected = timeseries[is_selected]

    #     add_px(fig_timeseries, px.area(timeseries_selected,
    #                                    color_discrete_sequence=['purple']))

    fig.update_layout(**fig_layout_kwargs)
    return fig 

def make_distribution_histogram_figure(distribution: pd.Series, x_limits: tuple[float, float],
                                       color: str) -> go.Figure:
    
    df_plot = pd.DataFrame(np.array([distribution, (distribution > 0)]).T, 
                           columns=['values', 'is_positive'])
    fig = px.histogram(data_frame=df_plot, 
                       x='values', 
                       nbins=30,
                       color='is_positive',
                       histnorm='percent', 
                       range_x=x_limits,
                       color_discrete_sequence=[color, 'black'])

    fig.update_layout(**fig_layout_kwargs, xaxis_title="return (%)", yaxis_title="")
    return fig

def make_distribution_scatter_figure(series_x: pd.Series, series_y: pd.Series,
                                     color_x: str, color_y: str) -> go.Figure:
    
    df = pd.DataFrame(np.array([series_x, series_y]).T, 
                      columns=['x', 'y'], index=series_x.index)
    df['x<y'] = series_x < series_y
    df['dates'] = df.index.to_series()
    
    min_val = min(min(series_x), min(series_y))
    max_val = max(max(series_x), max(series_y))
    
    fig = go.Figure(layout_xaxis_range=[min_val, max_val], layout_yaxis_range=[min_val, max_val])

    add_px(fig, px.scatter(df, x='x', y='y', custom_data=['dates'],
                           color='x<y',
                           color_discrete_sequence=[color_x, color_y]))

    fig.add_trace(go.Scatter(x=[min_val, max_val], y=[min_val, max_val],
                                mode='lines', line=dict(width=1)))

    fig.update_layout(**fig_layout_kwargs)
    return fig 

    