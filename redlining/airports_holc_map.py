import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

#airport data comes from https://ourairports.com/data/
data = pd.read_csv('data/input/us-airports.csv')
holc = gpd.read_file('data/input/mappinginequality.json')

holc['grade']  = np.where(holc['grade'] == 'C ', 'C', holc['grade'])
holc['grade']  = np.where(holc['grade'] == 'A ', 'A', holc['grade'])

#assuming that CRS is WGS84 because I honestly don't know
airports = gpd.GeoDataFrame(data, geometry = gpd.points_from_xy(data.longitude_deg, data.latitude_deg), crs = 'EPSG:4326')

###spatial join using predicate == within
holc_airports = holc.sjoin(airports, how = 'left', predicate = 'contains')
holc_airports = holc_airports.dropna(subset = ['name'])
holc_airports = holc_airports[holc_airports['type'] != 'heliport'].reset_index()

#125 airports fall within HOLC maps and are not heliports
holc_airports['grade'].hist(legend = True)
plt.savefig('data/output/holc_airport_grades')

#most of these airports are closed and the data is from a random site so nothing to hang a hat on but good sanity check that there is overlap between holc maps and airports and they are mostly in C and D areas