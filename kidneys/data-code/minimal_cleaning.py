import pandas as pd
import geopandas as gpd
import numpy as np

def clean_transplant(df):
    df[['city', 'state']] = df['location'].str.split(', ', expand=True)
    df = df[~df['state'].isin(['AK', 'HI'])]
    df.to_pickle('data/input/transplant_locations.pkl')
    print('transplant data cleaned')
    return df

def clean_dialysis(df):
    df = df[~df['State'].isin(['AK', 'HI'])]
    df['chain'] = np.where(df['Chain Owned'] == 'Yes', 1, 0)
    df['Chain Organization'] = df['Chain Organization'].str.lower()
    df['davita'] = np.where(df['Chain Organization'] == 'davita', 1, 0)
    df['fresenius'] = np.where(df['Chain Organization'] == 'fresenius medical care', 1, 0)
    df_state = df.groupby(['State', 'year']).agg('count')
    df_state.to_pickle('data/input/dialysis_state_panel.pkl')
    df.to_pickle('data/input/dialysis_panel_locations.pkl')
    print('dialysis panel cleaned')
    return df

def clean_county_ckd(ckd, counties):
    ckd = ckd[['StateAbbr', 'CountyName', 'CountyFIPS','KIDNEY_AdjPrev', "KIDNEY_CrudePrev","KIDNEY_Crude95CI","KIDNEY_Adj95CI"]]
    ckd = ckd[~ckd['StateAbbr'].isin(['AK', 'HI'])]

    counties['FIPS'] = counties['FIPS'].astype(int)
    counties = counties[~counties['STATE_NAME'].isin(['Alaska', 'Hawaii'])]
    counties.to_pickle('data/input/counties.pkl')

    ckd = pd.merge(ckd, counties, left_on = 'CountyFIPS', right_on = 'FIPS', how = 'left')
    ckd = gpd.GeoDataFrame(ckd, geometry='geometry')
    ckd = ckd.drop(columns = ['NAME', 'STATE_NAME', 'CNTY_FIPS'])
    ckd.to_pickle('data/input/ckd_county.pkl')
    print('ckd data cleaned')
    return ckd, counties

def clean_waitlist(df):
    df = df.replace({',':''}, regex=True).rename(columns = {'Unnamed: 0': 'State'}).drop(columns = ['Unnamed: 1', 'To Date'])
    cols_to_int = df.columns.drop('State')
    df[cols_to_int] = df[cols_to_int].astype(int)
    df = df.melt(id_vars = 'State', var_name = 'Year', value_name = 'Waitlist_Additions').iloc[1:].set_index(['State', 'Year']).sort_index()
    df.to_pickle('data/input/waitlist.pkl')
    print('waitlist data cleaned')
    return df

def clean_census(df):
    df['black'] = np.where(df['race'] == 2, 1, 0)
    df['white'] = np.where(df['race'] == 1, 1, 0)
    df['race_other'] = np.where(df['race'].isin([1, 2]), 0, 1)

    # ensure missing values are coded as such
    df.loc[df['empstat'].isin([0, 9]), 'empstat'] = np.nan
    df.loc[df['labforce'].isin([0, 9]), 'labforce'] = np.nan

    df['inctot'] = np.where(df['inctot'] < 0, 0, df['inctot'])
    df.loc[df['inctot'].isin([9999999, 0]), 'inctot'] = np.nan

    df['ftotinc'] = np.where(df['ftotinc'] < 0, 0, df['ftotinc'])
    df.loc[df['ftotinc'].isin([9999999, 0]), 'ftotinc'] = np.nan

    df.loc[df['poverty'] == 0, 'poverty'] = np.nan
    df['pov_thresh'] = np.where(df['poverty'] < 100, 1, 0) # dummy for being below 100% of family's poverty threshold

    # aggregate up to county level
    df['fips'] = df['statefip'].astype(str).str.cat(df['countyfip'].astype(str).str.zfill(3), sep='')
    df['fips'] = df['fips'].astype(int)
    df = df.groupby('fips').agg('mean').reset_index()
    print('census data cleaned')
    df.to_pickle('data/input/census_county.pkl')
    return df

def create_snapshot(census, ckd, dialysis_panel, transplant_locations):
    df = census.merge(ckd, left_on = 'fips', right_on = 'FIPS', how = 'outer')
    df = gpd.GeoDataFrame(df, geometry='geometry')

    # dialysis counts
    dialysis_2025 = dialysis_panel[dialysis_panel['year'] == 2025]
    dialysis = df.sjoin(dialysis_2025, how = 'left', predicate = 'contains')
    dialysis_counts = dialysis.groupby('FIPS')['Facility Name'].count().reset_index(name='dialysis_count')
    df = df.merge(dialysis_counts, on = 'FIPS', how = 'left')
    df['dialysis_count'] = df['dialysis_count'].fillna(0, inplace=True)

    # transplant counts
    transplant = df.sjoin(transplant_locations, how = 'left', predicate = 'contains')
    transplant_counts = transplant.groupby('FIPS')['name'].count().reset_index(name='transplant_count')
    df = df.merge(transplant_counts, on = 'FIPS', how = 'left') 
    df['transplant_count'] = df['transplant_count'].fillna(0, inplace=True)

    # dummy variable for dialysis or transplant presence
    df['any_dialysis'] = np.where(df['dialysis_count'] > 0, 1, 0)
    df['any_transplant'] = np.where(df['transplant_count'] > 0, 1, 0)
    df.to_pickle('data/input/snapshot_2025.pkl')
    print('snapshot created')
    return df

#######################################################################################################################

dialysis_panel = gpd.read_file('data/input/dialysis_panel_locations.geojson')
transplant_locations = gpd.read_file('data/input/transplant_locations.geojson')
ckd = pd.read_csv('data/input/ckd_county.csv')
counties = gpd.read_file('data/input/UScounties/UScounties.shp')
census = pd.read_pickle('data/input/census.pkl')
waitlist = pd.read_csv('data/input/waitlist_additions.csv')

transplant_locations = clean_transplant(transplant_locations)
dialysis_panel = clean_dialysis(dialysis_panel)
ckd, counties = clean_county_ckd(ckd, counties)
census_county = clean_census(census)
waitlist = clean_waitlist(waitlist)

# snapshot = create_snapshot(census_county, ckd, dialysis_panel, transplant_locations)