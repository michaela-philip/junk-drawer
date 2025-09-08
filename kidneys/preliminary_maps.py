import pandas as pd
import matplotlib.pyplot as plt

dialysis_panel = pd.read_pickle('data/intermed/dialysis_panel_locations.pkl')
counties = pd.read_pickle('data/intermed/counties.pkl')
transplant = pd.read_pickle('data/intermed/transplant_locations.pkl')
snapshot = pd.read_pickle('data/intermed/snapshot_2025.pkl')

# dissolve to county level
dialysis_county = dialysis_panel.dissolve(by = ['County', 'year'], aggfunc = 'sum').reset_index()
dialysis_county = counties.sjoin(dialysis_county, how = 'left', predicate = 'contains')
dialysis_county = dialysis_county.dropna(subset = 'year')
dialysis_county['year'] = dialysis_county['year'].astype(int)

dialysis_county['pct_chain'] = dialysis_county['chain'] / dialysis_county['count']
dialysis_county['pct_big2'] = (dialysis_county['davita'] + dialysis_county['fresenius']) / dialysis_county['count']

# facility counts
fig, axs = plt.subplots(2, 2, figsize = (12, 8))
panels = {(0,0):2018, (1,0):2020, (0,1):2022, (1,1):2024}
for key, value in panels.items():
    data = dialysis_county.loc[dialysis_county['year'] == value]
    ax = axs[key]
    vmax = data['count'].quantile(0.95)
    counties.boundary.plot(ax = ax, linewidth = 0.2, zorder = 1, color = 'black')
    data.plot('count', ax = ax, zorder = 2, legend = True, cmap = 'winter', vmin = 1, vmax = vmax, 
              missing_kwds={'color':'lightgrey'})
    ax.set_title(value)

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Dialysis Facilities over Time', y = 1)
plt.savefig('figures/facilities_map_trend.jpg')
# plt.show()

# percent chains
fig, axs = plt.subplots(2, 2, figsize = (12, 8))
panels = {(0,0):2018, (1,0):2020, (0,1):2022, (1,1):2024}
for key, value in panels.items():
    data = dialysis_county.loc[dialysis_county['year'] == value]
    ax = axs[key]
    counties.boundary.plot(ax = ax, linewidth = 0.2, zorder = 1, color = 'black')
    data.plot('pct_chain', ax = ax, zorder = 2, legend = True, cmap = 'winter', missing_kwds={'color':'lightgrey'})
    ax.set_title(value)

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Dialysis Chains over Time', y = 1)
plt.savefig('figures/pct_chain_map_trend.jpg')
# plt.show()

# percent chains
fig, axs = plt.subplots(2, 2, figsize = (12, 8))
panels = {(0,0):2018, (1,0):2020, (0,1):2022, (1,1):2024}
for key, value in panels.items():
    data = dialysis_county.loc[dialysis_county['year'] == value]
    ax = axs[key]
    counties.boundary.plot(ax = ax, linewidth = 0.2, zorder = 1, color = 'black')
    data.plot('pct_big2', ax = ax, zorder = 2, legend = True, cmap = 'winter', missing_kwds={'color':'lightgrey'})
    ax.set_title(value)

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Davita/Fresenius Facilities over Time', y = 1)
plt.savefig('figures/pct_chain_map_trend.jpg')
# plt.show()

# dialysis facilities and transplant centers
fig, ax = plt.subplots()
data = dialysis_panel.loc[dialysis_panel['year'] == 2025]
counties.boundary.plot(ax = ax, linewidth = 0.2, zorder = 3, color = 'black')
data.plot(ax = ax, color = 'tab:red', legend = True, markersize = 2, zorder = 1, label = 'Dialysis Centers')
transplant.plot(ax = ax, color = 'tab:blue', legend = True, markersize = 5, zorder = 2, label = 'Transplant Centers')
legend = ax.legend(loc = 'lower left')
ax.set_axis_off()
fig.tight_layout()
fig.suptitle('Dialysis and Transplant Centers (2025)')
plt.savefig('figures/dialysis_transplant_map.jpg')
plt.show()

# snapshot
fig, ax = plt.subplots()
counties.boundary.plot(ax = ax, linewidth = 0.2, zorder = 4, color = 'black')
counties.plot(ax = ax, linewidth = 0.2, color = 'lightgrey', zorder = 1)
snapshot.plot(ax = ax, cmap = 'Blues', column = 'KIDNEY_CrudePrev', zorder = 2)
transplant.plot(ax = ax, color = 'gold', legend = True, markersize = 5, marker = '*', zorder = 3, label = 'Transplant Centers')
data = dialysis_panel.loc[dialysis_panel['year'] == 2025]
data.plot(ax = ax, color = 'tab:red', legend = True, markersize = 0.5, zorder = 2, label = 'Dialysis Centers')
legend = ax.legend(loc = 'lower left')
# add colorbar for CKD prevalence
sm = plt.cm.ScalarMappable(
    cmap='Blues',
    norm=plt.Normalize(vmin=snapshot['KIDNEY_CrudePrev'].min(),
                       vmax=snapshot['KIDNEY_CrudePrev'].max())
)
sm._A = []  # needed for matplotlib < 3.6
cbar = fig.colorbar(sm, ax=ax, orientation = 'horizontal')
cbar.set_label('CKD Prevalence (%)')
ax.set_axis_off()
fig.tight_layout()
fig.suptitle('CKD Prevalence, Dialysis and Transplant Centers (2025)')
plt.savefig('figures/snapshot_map.jpg')
plt.show()