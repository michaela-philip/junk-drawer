import pandas as pd
import geopandas as gpd
import gzip

colspecs = [(0, 4), (4, 10), (10, 18), (18, 31), (31, 41), (41, 54), (54, 56), (56, 60), (60, 72), (72, 73), (73, 77), 
            (77, 87), (87, 88), (88, 91), (91, 92), (92, 94), (94, 95), (95, 102), (102, 109), (109, 112)]
columns = ['year', 'sample', 'serial', 'cbserial', 'hhwt', 'cluster', 'stateicp', 'countyicp', 'strata', 'gq', 
           'pernum', 'perwt', 'race', 'raced', 'empstat', 'empstatd', 'labforce', 'inctot', 'ftotinc', 'poverty']

census = pd.read_fwf(gzip.open('data/input/usa_00006.dat.gz'), colspecs = colspecs, header = None, columns = columns)
census.to_pickle('data/input/census.pkl')

icpsr_crosswalk = pd.read_csv('data/input/icpsrcnt.csv', dtype = str)