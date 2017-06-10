from bokeh.plotting import figure
from bokeh.io import curdoc, output_file, show
from bokeh.layouts import layout, widgetbox
from bokeh.models import Div, HoverTool, TapTool, PanTool, WheelZoomTool,\
                         BoxZoomTool, ResetTool, ResizeTool, OpenURL
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models.tiles import WMTSTileSource
from bokeh.tile_providers import STAMEN_TERRAIN
from collections import OrderedDict
from bokeh.models.widgets import Select, MultiSelect, Slider, TextInput
import pyproj
import pandas as pd


def set_maprange(xmin, ymin, xmax, ymax, epsg_in='epsg:4326'):
    """
    Convert lat/lon coordinates into a format readable by bokeh
    Return converted min and max extend of the map
    """
    outProj = pyproj.Proj(init='epsg:3857')
    inProj = pyproj.Proj(init=epsg_in)
    xmin,ymin = 75, -55
    xmax,ymax = 175, -5
    x1,y1 = pyproj.transform(inProj,outProj,xmin,ymin)
    x2,y2 = pyproj.transform(inProj,outProj,xmax,ymax)
    return x1, y1, x2, y2


def display_map(datasource, location_lon, location_lat):
    west, south = 75, -55
    east, north = 175, -5
    westmax, southmax, eastmax, northmax = set_maprange(west, south, east, north)
    # Initialize map
    mapfig = figure(tools='pan, hover, tap, box_zoom, reset, wheel_zoom',
                 x_range=(westmax, eastmax),
                 y_range=(southmax, northmax), width=700, height=400)
    mapfig.axis.visible = False
    mapfig.add_tile(STAMEN_TERRAIN)

    hover = mapfig.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([('Name', '@common_name'),('species', '@species'),
                                  ('Date', '@eventdate')])
    output_file("wildlife_plot.html")
    mapfig.circle(x="lon", y="lat", source=datasource, size=5, color="color", alpha=0.7)
    return mapfig


def display_lineplot(datasource, controls):
    p = figure(title="sightings count of selected family in Australia",
               plot_width=500, plot_height=200)
    p.line(x="year", y="common_name", source=datasource)
    return p


def widget_controls(df):
    fromYear = Select(title="Sightings since Year", value='1990',
                      options=sorted(list(pd.unique(df['year']))))
    family = MultiSelect(title="Family", value=["Balaenopteridae"],
                         options=list(pd.unique(df['family'])))
    radius = Slider(title='Search Radius', start=50, end=1000, value=150, step=50)
    location = TextInput(value="Sydney", title="Location:")
    return fromYear, family, radius, location


def html_hyperlink(species):
    text = ""
    i = 1
    for item in species:
        if isinstance(item, str):
            if i % 3 != 0:
                text += "<a href = 'https://en.wikipedia.org/wiki/%s' target='_blank'>%s</a> &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp" %(item, item)
                i += 1
            else:
                text += "<br>"
                i += 1
    return text