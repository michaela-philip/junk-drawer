import pandas as pd
import gzip

colspecs = [(0, 4), (4, 8), (8, 14), (14, 22), (22, 35), (35, 45), (45, 58), (58, 60), (60, 63), (63, 75), (75, 76), 
            (76, 80), (80, 90), (90, 91), (91, 94), (94, 95), (95, 97), (97, 98), (98, 105), (105, 112), (112, 115)]
columns = ['year', 'multyear', 'sample', 'serial', 'cbserial', 'hhwt', 'cluster', 'statefip', 'countyfip', 'strata', 'gq', 
           'pernum', 'perwt', 'race', 'raced', 'empstat', 'empstatd', 'labforce', 'inctot', 'ftotinc', 'poverty']

census = pd.read_fwf(gzip.open('data/input/usa_00008.dat.gz'), colspecs = colspecs, header = None, names = columns)
census.to_pickle('data/input/census.pkl')