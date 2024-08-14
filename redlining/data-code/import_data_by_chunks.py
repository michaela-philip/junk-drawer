import pandas as pd
import gzip
import numpy as np

ed_census_xwalk = pd.read_csv('data/input/enumdist_centract_xwalk.csv')
print('crosswalk loaded')

colspecs = [(0, 4), (4, 10), (10, 18), (18, 28), (28, 30), (30, 32), (32, 36), (36, 37), (37, 38), (38, 40), (40, 49), (49, 53), (53, 63), (63, 64), (64, 67), (67, 71), (71, 77), (77, 79), (79, 115)]
columns = ['year', 'sample', 'serial', 'hhwt', 'stateicp', 'statefip', 'countyicp', 'gq', 'ownershp', 'ownershpd', 'enumdist', 'pernum', 'perwt', 'race', 'raced', 'occ', 'incwage', 'versionhist', 'histid']

ipums_list = []

with gzip.open('data/input/usa_00004.dat.gz', 'rb') as f:
    for chunk in pd.read_fwf(f, colspecs=colspecs, header=None, chunksize=100000):
        chunk.columns = columns
        chunk['ownershp'] = np.where(chunk['ownershp'] == 1, 1, 0)
        ipums_inter = chunk.merge(ed_census_xwalk, how='right', on=['enumdist', 'countyicp', 'stateicp'])
        ipums_inter = ipums_inter.dropna(subset=['ownershp'])
        ipums_list.append(ipums_inter)
        del chunk, ipums_inter

ipums = pd.concat(ipums_list)
print('merge complete')
print('size is', ipums.shape)

ipums_agg = ipums.groupby(['gisjoin', 'stateicp', 'countyicp']).agg({'ownershp': 'mean', 'incwage': 'mean'}).reset_index()
ipums_agg.to_csv('data/output/ipums_agg.csv')
print('aggregate csv created')
print(ipums_agg.shape)