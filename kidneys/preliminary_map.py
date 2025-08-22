import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
counties.boundary.plot(ax = ax, color = 'black', linewidth = 0.2)
ckd.plot(column = 'KIDNEY_AdjPrev', ax = ax, legend = True, cmap = 'Greens')
dialysis_locations.plot(ax=ax, color = 'red', markersize = 1, label = 'Dialysis Centers', alpha=0.8)
transplant_locations.plot(ax=ax, color = 'blue', markersize = 5, label = 'Transplant Centers')
xmin, ymin, xmax, ymax = counties.total_bounds
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_aspect('equal')
plt.show()