import pandas as pd
print('pandas in')
import numpy as np
print('numpy in')

import gzip
print('gzip in')

colspecs = [(0, 4), (4, 10), (10, 18), (18, 28), (28, 30), (30, 32), (32, 36), (36, 37), (37, 38), (38, 40), (40, 49), (49, 53), (53, 63), (63, 64), (64, 67), (67, 71), (71, 77), (77, 79), (79, 115)]
columns = ['year', 'sample', 'serial', 'hhwt', 'stateicp', 'statefip', 'countyicp', 'gq', 'ownershp', 'ownershpd', 'enumdist', 'pernum', 'perwt', 'race', 'raced', 'occ', 'incwage', 'versionhist', 'histid']

# with gzip.open('data/input/usa_00004.dat', 'rb') as f:
#     df = pd.read_fwf(f, colspecs = colspecs, header = None)
#     print('census data loaded')
    
data = 'data/input/usa_00004.dat'
df = pd.read_fwf(data, colspecs = colspecs, header = None)
print('census data loaded')

df.columns = columns
df['ownershp'] = np.where(df['ownershp'] == 1, 1, 0)

ed_census_xwalk = pd.read_csv('data/input/enumdist_centract_xwalk.csv')
print('crosswalk loaded')

ipums = df.merge(ed_census_xwalk, how= 'right', on = ['enumdist', 'countyicp', 'stateicp'])
print('merge complete')
ipums = ipums.dropna(subset=['ownershp'])

ipums.to_csv('data/output/ipums.csv')
print('csv created')
print(ipums.shape)

ipums_agg = ipums.groupby(['stateicp', 'countyicp']).agg({'ownershp': 'mean', 'gisjoin': 'first', 'perwt': 'mean','incwage': 'mean'}).reset_index()
ipums_agg.to_csv('data/output/ipums_agg.csv')
print('aggregate csv created')
print(ipums_agg.shape)
