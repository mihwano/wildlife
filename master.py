import data
import gui
import pandas as pd
from bokeh.layouts import layout, widgetbox
from bokeh.io import show, curdoc
from bokeh.plotting import show
from bokeh.models import Div


url = '/home/gilles/projects/wildlife/aus_cetacae.csv'
df, source, source.data = data.datasource_map(url)
hyperlinks = Div(text=gui.html_hyperlink(list(pd.unique(df['species']))), width=600)

dfplot, sourceplot, sourceplot.data = data.datasource_plot(df)

controls = list(gui.widget_controls(df))
for control in controls:
    control.on_change('value', lambda attr, old,
                      new: data.update_map(df, source, controls))
for control in controls:
    control.on_change('value', lambda attr, old,
                      new: data.update_plot(dfplot, sourceplot, controls))

location_lon, location_lat = data.transform_coords(
                                data.coordinates_from_location(controls[3].value).longitude,
                                data.coordinates_from_location(controls[3].value).latitude,
                                'epsg:4326')

mapfig = gui.display_map(source, location_lon, location_lat)
plotfig = gui.display_lineplot(sourceplot, controls)

inputs = widgetbox(*controls, sizing_mode='fixed')

l = layout([
        [mapfig, inputs],
        [plotfig, hyperlinks]
    ], sizing_mode='fixed')

data.update_plot(dfplot, sourceplot, controls)
data.update_map(df, source, controls)

curdoc().add_root(l)
#show(l)
