import pandas as pd
import sys
import os

# script_dir = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(script_dir, '..'))

import gzip

colspecs = [(0, 4), (4, 10), (10, 18), (18, 28), (28, 30), (30, 32), (32, 36), (36, 37), (37, 38), (38, 40), (40, 49), (49, 53), (53, 63), (63, 64), (64, 67), (67, 71), (71, 77), (77, 79), (79, 115)]
columns = ['year', 'sample', 'serial', 'hhwt', 'stateicp', 'statefip', 'countyicp', 'gq', 'ownershp', 'ownershpd', 'enumdist', 'pernum', 'perwt', 'race', 'raced', 'occ', 'incwage', 'versionhist', 'histid']

with gzip.open('data/input/usa_00004.dat.gz', 'rb') as f:
    df = pd.read_fwf(f, colspecs = colspecs, header = None, nrows = 3000000)
df.columns = columns

ed_census_xwalk = pd.read_csv('data/input/enumdist_centract_xwalk.csv')

ipums = df.merge(ed_census_xwalk, how= 'right', on = ['enumdist', 'countyicp', 'stateicp'])
ipums = ipums.dropna(subset=['ownershp'])

ipums.to_csv('data/output/ipums.csv')
print('csv created')
print(ipums.size())