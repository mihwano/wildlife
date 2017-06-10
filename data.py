import pandas as pd
import bokeh
import numpy as np
from datetime import datetime
from bokeh.models import ColumnDataSource
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import requests
import io
import pyproj
import pdb

def load_data(url):
    return pd.read_csv(url, sep='\t')


def name_mapping():
    return {'Megaptera novaeangliae':'humpback whale',
           'Physeter macrocephalus':'cachalot',
           'Orcinus orca':'killer whale',
           'Pseudorca crassidens':'false killer whale',
           'Stenella coeruleoalba':'striped dolphin',
           'Tursiops truncatus':'common bottlenose dolphin',
           'Stenella longirostris':'spinner dolphin',
           'Peponocephala electra':'electra dolphin',
           'Dugong dugon':'dugong',
           'Balaenoptera acutorostrata':'common minke whale',
           'Eubalaena australis':'southern right whale',
           'Globicephala melas':'long-finned pilot whale',
           'Balaenoptera musculus':'blue whale',
           'Balaenoptera physalus':'fin whale',
           'Globicephala macrorhynchus':'short-finned pilot whale',
           'Balaenoptera borealis':'sei whale',
           'Delphinus delphis':'short-beaked common dolphin',
           'Balaenoptera edeni':'bryde\'s whale',
           'Grampus griseus':'risso\'s dolphin',
           'Feresa attenuata':'pygmy killer whale',
           'Hyperoodon planifrons':'southern bottlenose whale',
           'Caperea marginata':'pygmy right whale',
           np.nan:''}


def species_colormap():
    return {'Balaenopteridae':'blue',
            'Physeteridae':'yellow',
            'Delphinidae':'red',
            'Dugongidae':'purple',
            'Balaenidae':'blue',
            'Hyperoodontidae':'green',
            'Neobalaenidae':'blue'}


def eventdates(df):
    df = df[~df['eventdate'].isnull()]
    df['eventdate'] = [datetime.strptime(x, "%Y-%m-%dT%H:%MZ") for x in df['eventdate']]
    df['dayofweek'] = [x.strftime('%A') for x in df['eventdate']]
    df['month'] = [x.strftime('%B') for x in df['eventdate']]
    df['year'] = [x.strftime('%Y') for x in df['eventdate']]
    df['dayofmonth'] = [x.day for x in df['eventdate']]
    return df


def transform_coords(x, y, epsg_in):
    outProj = pyproj.Proj(init='epsg:3857')
    inProj = pyproj.Proj(init=epsg_in)
    return pyproj.transform(inProj, outProj, x, y)


def datasource_map(url, epsg_in='epsg:4326'):
    df = load_data(url)

    df['common_name'] = [name_mapping()[x] for x in df['species']]

    df = eventdates(df)

    df = df[['order', 'family', 'species', 'common_name', 'decimallatitude',
             'decimallongitude', 'eventdate', 'dayofmonth','dayofweek', 'month', 'year']]

    df['color'] = [species_colormap()[x] for x in df['family']]

    df['lon'], df['lat'] = transform_coords(df['decimallongitude'].values,
                                            df['decimallatitude'].values,
                                            epsg_in)
    df['eventdate'] = [str(x)[:10] for x in df['eventdate']]

    df['link'] = [x.replace(' ', '_') if isinstance(x, str) else\
                  'cetacea' for x in df['species']]

    source = ColumnDataSource(data=dict(decimallatitude=[], decimallongitude=[],
                              common_name=[], species=[], color=[], link=[]))
    source.data = source.from_df(df[['lon', 'lat', 'eventdate', 'common_name',
                                     'species', 'color', 'link']])
    return df, source, source.data

 
def datasource_plot(df):
    source = ColumnDataSource(data=dict(year=[], common_name=[]))
    source.data = source.from_df(df[['year', 'common_name']])
    return df, source, source.data  


def coordinates_from_location(name):
    geolocator = Nominatim()
    return geolocator.geocode(name + " Australia")    


def calculate_distances(x, y, name, epsg_in):
    lon = coordinates_from_location(name).longitude
    lat = coordinates_from_location(name).latitude
    distance = [great_circle((lat, lon), coord).miles for coord in list(zip(y, x))]
    return distance


def select_slice(df, controls, epsg_in):
    fromYear_val = controls[0].value
    family_val = controls[1].value
    radius_val = controls[2].value
    location_val = controls[3].value
    df['year'] = [int(x) for x in df['year']]
    selected = df[(df['year'] >= int(fromYear_val)) & (df['family'].isin(family_val))]
    distance = calculate_distances(selected['decimallongitude'].values,
                                   selected['decimallatitude'].values,
                                   location_val, epsg_in)
    selected['distance'] = distance
    selected = selected[selected['distance'] <= radius_val]
    selected['year'] = [str(x) for x in selected['year']]
    return selected


def update_map(df, source, controls, epsg_in='epsg:4326'):
    newdf = select_slice(df, controls, epsg_in)
    source.data = source.from_df(newdf[['lon', 'lat', 'eventdate', 'common_name',
                                     'species', 'color', 'link']])
    return source.data


def update_plot(df, sourceplot, controls):
    plotdf = df[df['family'].isin(controls[1].value)] 
    ds = plotdf.groupby(['family', 'year'], as_index=False)['common_name'].count()
    sourceplot.data = sourceplot.from_df(ds[['year', 'common_name']])
    return sourceplot.data