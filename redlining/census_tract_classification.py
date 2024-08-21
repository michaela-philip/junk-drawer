import pandas as pd
import geopandas as gpd
import numpy as np

holc = gpd.read_file('data/input/mappinginequality.json')
holc = holc.to_crs('ESRI:102003')
holc['grade']  = np.where(holc['grade'] == 'C ', 'C', holc['grade'])
holc['grade']  = np.where(holc['grade'] == 'A ', 'A', holc['grade'])

nhgis = gpd.read_file('data/input/Census Tract 1940/US_tract_1940_conflated.shp')
nhgis.rename(columns={'GISJOIN': 'gisjoin'}, inplace=True)

ipums = pd.read_csv('data/output/ipums_agg.csv')
ipums.drop(ipums.columns[0], axis=1, inplace=True)

nhgis_ipums = nhgis.merge(ipums, on = 'gisjoin')
holc_ipums = nhgis_ipums.overlay(holc, how = 'identity', keep_geom_type = False)

def classify_ct(data, holc):
    polygons = data.overlay(holc, how = 'identity', keep_geom_type = False)
    polygons['grade'].fillna()
    polygons.to_crs('EPSG:32610')
    polygons['area'] = polygons['geometry'].area
    polygons['area_A'] = np.where(polygons['grade'] == 'A', polygons['area'], 0)
    polygons['area_B'] = np.where(polygons['grade'] == 'B', polygons['area'], 0)
    polygons['area_C'] = np.where(polygons['grade'] == 'C', polygons['area'], 0)
    polygons['area_D'] = np.where(polygons['grade'] == 'D', polygons['area'], 0)

    tract = polygons.groupby(['gisjoin', 'countyicp', 'stateicp', 'TRACT', 'ownershp'])[['area', 'area_A', 'area_B', 'area_C', 'area_D']].sum().reset_index()

    tract['pct_A'] = tract['area_A'] / tract['area']
    tract['pct_B'] = tract['area_B'] / tract['area']
    tract['pct_C'] = tract['area_C'] / tract['area']
    tract['pct_D'] = tract['area_D'] / tract['area']

