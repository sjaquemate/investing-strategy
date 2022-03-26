from dash import dcc
import dash_bootstrap_components as dbc


def rangeslider(id, min_value, max_value, tick_step, min_pushable):
    return dcc.RangeSlider(id=id,
        min=min_value, max=max_value, value=[min_value, max_value],
        marks={year: str(year) for year in range(min_value, max_value, tick_step)},
        step=1, dots=False,
        pushable=min_pushable, updatemode='mouseup',
        tooltip={'placement': 'top', 'always_visible': True}
    )
    
def dropdown(id, options, default_value):
    return dcc.Dropdown(id=id, options=options, value=default_value, clearable=False)
  
def badgebutton(text, id):
    return dbc.Badge(text, id=id, style={'cursor': 'pointer'})
    