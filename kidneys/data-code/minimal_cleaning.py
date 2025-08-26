import pandas as pd
import geopandas as gpd
import numpy as np

# general cleanup and pickle individual datasets (easier to map)
transplant_locations = gpd.read_file('data/input/transplant_locations.geojson')
transplant_locations[['city', 'state']] = transplant_locations['location'].str.split(', ', expand=True)
transplant_locations = transplant_locations[~transplant_locations['state'].isin(['AK', 'HI'])]
transplant_locations.to_pickle('data/input/transplant_locations.pkl')

dialysis_locations = gpd.read_file('data/input/dialysis_locations.geojson')
dialysis_locations = dialysis_locations[['CMS Certification Number (CCN)', 'Network', 'Facility Name', 
                                         'Address Line 1', 'Address Line 2', 'City/Town', 'State', 'ZIP Code','geometry']]
dialysis_locations = dialysis_locations[~dialysis_locations['State'].isin(['AK', 'HI'])]
dialysis_locations.to_pickle('data/input/dialysis_locations.pkl')

ckd = pd.read_csv('data/input/ckd_county.csv')
ckd = ckd[['StateAbbr', 'CountyName', 'CountyFIPS','KIDNEY_AdjPrev', "KIDNEY_CrudePrev","KIDNEY_Crude95CI","KIDNEY_Adj95CI"]]
ckd = ckd[~ckd['StateAbbr'].isin(['AK', 'HI'])]

counties = gpd.read_file('data/input/UScounties/UScounties.shp')
counties['FIPS'] = counties['FIPS'].astype(int)
counties = counties[~counties['STATE_NAME'].isin(['Alaska', 'Hawaii'])]
counties.to_pickle('data/input/counties.pkl')

ckd = pd.merge(ckd, counties, left_on = 'CountyFIPS', right_on = 'FIPS', how = 'left')
ckd = gpd.GeoDataFrame(ckd, geometry='geometry')
ckd = ckd.drop(columns = ['NAME', 'STATE_NAME', 'CNTY_FIPS'])
ckd.to_pickle('data/input/ckd_county.pkl')

### CLEAN UP CENSUS DATA ###
census = pd.read_pickle('data/input/census.pkl')

# make race dummy variables
census['black'] = np.where(census['race'] == 2, 1, 0)
census['white'] = np.where(census['race'] == 1, 1, 0)
census['race_other'] = np.where(census['race'].isin([1, 2]), 0, 1)

# ensure missing values are coded as such
census.loc[census['empstat'].isin([0, 9]), 'empstat'] = np.nan
census.loc[census['labforce'].isin([0, 9]), 'labforce'] = np.nan

census['inctot'] = np.where(census['inctot'] < 0, 0, census['inctot'])
census.loc[census['inctot'].isin([9999999, 0]), 'inctot'] = np.nan

census['ftotinc'] = np.where(census['ftotinc'] < 0, 0, census['ftotinc'])
census.loc[census['ftotinc'].isin([9999999, 0]), 'ftotinc'] = np.nan

census.loc[census['poverty'] == 0, 'poverty'] = np.nan
census['pov_thresh'] = np.where(census['poverty'] < 100, 1, 0) # dummy for being below 100% of family's poverty threshold

# aggregate up to county level
census['fips'] = census['statefip'].astype(str).str.cat(census['countyfip'].astype(str).str.zfill(3), sep='')
census['fips'] = census['fips'].astype(int)
census = census.groupby('fips').agg('mean').reset_index()

# combine all data into one df
df = census.merge(ckd, left_on = 'fips', right_on = 'FIPS', how = 'outer')
df = gpd.GeoDataFrame(df, geometry='geometry')

# spatial join to get location counts, then merge in counts
dialysis = df.sjoin(dialysis_locations, how = 'left', predicate = 'contains')
dialysis_counts = dialysis.groupby('FIPS')['Facility Name'].count().reset_index(name='dialysis_count')
df = df.merge(dialysis_counts, on = 'FIPS', how = 'left')
df['dialysis_count'] = df['dialysis_count'].fillna(0)

transplant = df.sjoin(transplant_locations, how = 'left', predicate = 'contains')
transplant_counts = transplant.groupby('FIPS')['name'].count().reset_index(name='transplant_count')
df = df.merge(transplant_counts, on = 'FIPS', how = 'left') 
df['transplant_count'] = df['transplant_count'].fillna(0)

# dummy variable for dialysis or transplant presence
df['any_dialysis'] = np.where(df['dialysis_count'] > 0, 1, 0)
df['any_transplant'] = np.where(df['transplant_count'] > 0, 1, 0)

df.to_pickle('data/input/cleaned_data.pkl')