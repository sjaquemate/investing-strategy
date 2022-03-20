from dash import dcc

def range_slider(id, min_value, max_value, tick_step, min_pushable):
    return dcc.RangeSlider(id=id,
        min=min_value, max=max_value, value=[min_value, max_value],
        marks={year: str(year) for year in range(min_value, max_value, tick_step)},
        step=1, dots=False,
        pushable=min_pushable, updatemode='mouseup',
        tooltip={'placement': 'top', 'always_visible': True}
    )