import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

#import and minor cleanup
holc = gpd.read_file('data/input/mappinginequality.json')
holc = holc.to_crs('ESRI:102003')
holc['grade']  = np.where(holc['grade'] == 'C ', 'C', holc['grade'])
holc['grade']  = np.where(holc['grade'] == 'A ', 'A', holc['grade'])

nhgis = gpd.read_file('data/input/Census Tract 1940/US_tract_1940_conflated.shp')
nhgis.rename(columns={'GISJOIN': 'gisjoin'}, inplace=True)

ipums = pd.read_csv('data/output/ipums_agg.csv')
ipums.drop(ipums.columns[0], axis=1, inplace=True)

nhgis_ipums = nhgis.merge(ipums, on = 'gisjoin')

#create a map for each grade
holc_A = holc[holc['grade'] == 'A']
holc_B = holc[holc['grade'] == 'B']
holc_C = holc[holc['grade'] == 'C']
holc_D = holc[holc['grade'] == 'D']

#spatial merge per grade
own_A = nhgis_ipums.sjoin(holc_A, predicate = 'contains', how = 'inner')
own_B = nhgis_ipums.sjoin(holc_B, predicate = 'contains', how = 'inner')
own_C = nhgis_ipums.sjoin(holc_C, predicate = 'contains', how = 'inner')
own_D = nhgis_ipums.sjoin(holc_D, predicate = 'contains', how = 'inner')

#immediate info in histogram
fig, axes = plt.subplots(2, 2, sharey=True)
ax1, ax2, ax3, ax4 = axes.flatten()
own_A['ownershp'].hist(ax=ax1)
own_B['ownershp'].hist(ax=ax2)
own_C['ownershp'].hist(ax=ax3)
own_D['ownershp'].hist(ax=ax4)
ax1.set_title('Grade A')
ax2.set_title('Grade B')
ax3.set_title('Grade C')
ax4.set_title('Grade D')
plt.subplots_adjust(hspace=0.4)
fig.suptitle('Home Ownership Rates by HOLC Grade')
fig.savefig('data/output/Home Ownership Histogram.png')

#TODO
#actually map out the data
counties = gpd.read_file('data/input/US County Boundaries/us-county-boundaries.shp')
counties.to_crs('ESRI:102003')
states = counties.dissolve(by='statefp')

base = states.boundary.plot(edgecolor='black', zorder = 2)
map_A = own_A.plot(column='ownershp', ax = base, figsize = (15, 20), zorder=1)

minx, miny, maxx, maxy  = own_A.total_bounds
base.set_xlim(minx, maxx)
base.set_ylim(miny, maxy)

plt.show()