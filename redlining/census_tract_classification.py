import pandas as pd
import geopandas as gpd
import numpy as np

holc = gpd.read_file('redlining/data/input/mappinginequality.json')
holc = holc.to_crs('ESRI:102003')
holc['grade']  = np.where(holc['grade'] == 'C ', 'C', holc['grade'])
holc['grade']  = np.where(holc['grade'] == 'A ', 'A', holc['grade'])

nhgis = gpd.read_file('redlining/data/input/Census Tract 1940/US_tract_1940_conflated.shp')
nhgis.rename(columns={'GISJOIN': 'gisjoin'}, inplace=True)

ipums = pd.read_csv('redlining/data/output/ipums_agg.csv')
ipums.drop(ipums.columns[0], axis=1, inplace=True)

nhgis_ipums = nhgis.merge(ipums, on = 'gisjoin')

def classify_ct(data, holc, threshold):
    #polygons should be subsections of tracts that fall within one HOLC grade only
    polygons = data.overlay(holc, how = 'identity', keep_geom_type = False)
    polygons.to_crs('EPSG:32610')
    polygons['area'] = polygons['geometry'].area

    #assign each area measurement to its grade so that we can aggregate
    polygons['area_A'] = np.where(polygons['grade'] == 'A', polygons['area'], 0)
    polygons['area_B'] = np.where(polygons['grade'] == 'B', polygons['area'], 0)
    polygons['area_C'] = np.where(polygons['grade'] == 'C', polygons['area'], 0)
    polygons['area_D'] = np.where(polygons['grade'] == 'D', polygons['area'], 0)
    polygons['area_U'] = np.where(~polygons['grade'].isin(['A', 'B', 'C', 'D']), polygons['area'], 0)  
    
    if not (polygons['area_A'] + polygons['area_B'] + polygons['area_C'] + polygons['area_D'] + polygons['area_U']).sum() == polygons['area'].sum():
        raise ValueError(f"Sum of areas for TRACT {polygons['TRACT']} are incorrect")    
    
    #aggregate up to the census tract level, summing up total area in each grade and overall 
    #note that gisjoin, TRACT, and ownershp should all be at the census tract level, state and county are above -> resulting df should be the same size as initial data
    tract = polygons.groupby(['gisjoin', 'countyicp', 'stateicp', 'TRACT', 'ownershp'])[['area', 'area_A', 'area_B', 'area_C', 'area_D', 'area_U']].sum().reset_index()

    #want to drop census tracts that are below some threshold of HOLC coverage
    tract['pct_U'] = tract['area_U'] / tract['area']
    tract = tract[tract['pct_U'] <= threshold].reset_index()

    #recalculate the area without Uncategorized land so that percentages of the 4 grades add up to 1
    tract['area'] = tract['area'] - tract['area_U']

    #calculate percentage of each tract that belongs to each grade
    tract['pct_A'] = tract['area_A'] / tract['area']
    tract['pct_B'] = tract['area_B'] / tract['area']
    tract['pct_C'] = tract['area_C'] / tract['area']
    tract['pct_D'] = tract['area_D'] / tract['area']

    #function to classify each tract as one of 10 primary/secondary grades
    def assign_grade_10(row):
        # Only or mainly A
        if row['pct_A'] > max(row['pct_B'], row['pct_C'], row['pct_D']):
            return 'A'
        # Mainly B, some A
        elif row['pct_B'] > max(row['pct_A'], row['pct_C'], row['pct_D']) and row['pct_A'] > 0:
            return 'B_A'
        # Only B
        elif row['pct_B'] > 0.99:
            return 'B'
        # Mainly C or D, some A
        elif (row['pct_C'] > max(row['pct_A'], row['pct_B'], row['pct_D']) and row['pct_A'] > 0) or (row['pct_D'] > max(row['pct_A'], row['pct_B'], row['pct_C']) and row['pct_A'] > 0):
            return 'CD_A'
        # Mainly B, some C or D
        elif row['pct_B'] > max(row['pct_A'], row['pct_C'], row['pct_D']) and (row['pct_C'] > 0 or row['pct_D'] > 0):
            return 'B_CD'
        # Only C
        elif row['pct_C'] > 0.99:
            return 'C'
        # Mainly C or D, some B
        elif (row['pct_C'] > max(row['pct_A'], row['pct_B'], row['pct_D']) and row['pct_B'] > 0) or (row['pct_D'] > max(row['pct_A'], row['pct_B'], row['pct_C']) and row['pct_B'] > 0):
            return 'CD_B'
        # Only D
        elif row['pct_D'] > 0.99:
            return 'D'
        # Mainly C, some D
        elif row['pct_C'] > max(row['pct_A'], row['pct_B'], row['pct_D']) and row['pct_D'] > 0:
            return 'C_D'
        # Mainly D, some C
        elif row['pct_D'] > max(row['pct_A'], row['pct_B'], row['pct_C']) and row['pct_C'] > 0:
            return 'D_C'
        else:
            print(f"Tract {row['TRACT']} doesn't fit a category because A = {row['pct_A']}, B = {row['pct_B']}, C = {row['pct_C']}, D = {row['pct_D']}, U = {row['pct_U']}")
            return None
    
    #function to classify asone of 4 primary grades
    def assign_grade_4(row):
        # Only or mainly A
        if row['pct_A'] > max(row['pct_B'], row['pct_C'], row['pct_D']):
            return 'A'
        if row['pct_B'] > max(row['pct_A'], row['pct_C'], row['pct_D']):
            return 'B'
        if row['pct_C'] > max(row['pct_A'], row['pct_B'], row['pct_D']):
            return 'C'
        if row['pct_D'] > max(row['pct_A'], row['pct_B'], row['pct_C']):
            return 'D'
        else:
            print(f"Tract {row['TRACT']} doesn't fit a category because A = {row['pct_A']}, B = {row['pct_B']}, C = {row['pct_C']}, D = {row['pct_D']}, U = {row['pct_U']}")
            return None

    #calculate grades for each tract
    tract['grade_10'] = tract.apply(assign_grade_10, axis = 1)
    tract['grade_4'] = tract.apply(assign_grade_4, axis = 1)
    return tract

tract = classify_ct(nhgis_ipums, holc, 0.05)

tract_by_grade_10 = tract.groupby('grade_10')['ownershp'].agg(['min', 'max', 'mean', 'median']).reset_index()
tract_by_grade_4 = tract.groupby('grade_4')['ownershp'].agg(['min', 'max', 'mean', 'median']).reset_index()