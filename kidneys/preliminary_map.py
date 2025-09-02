import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

dialysis_state = pd.read_pickle('data/intermed/dialysis_state_panel.pkl')
waitlist = pd.read_pickle('data/intermed/waitlist.pkl')

dialysis_state = dialysis_state.rename(columns = {'Facility Name':'facilities', 'State':'state', 'Year':'year'})
waitlist = waitlist.rename(columns = {'Waitlist_Additions':'waitlist_additions', 'Abbr':'state', 'Year':'year'})
waitlist['year'] = waitlist['year'].astype(int)
dialysis_state = dialysis_state.merge(waitlist, on = ['state', 'year'], how = 'left')

### REGIONAL LEVEL ###
df = dialysis_state.groupby(['Region', 'year']).agg('sum').reset_index().drop(columns = ['state', 'State'])
df['pct_chain'] = df['chain'] / df['facilities']
df['pct_big2'] = (df['davita'] + df['fresenius']) / df['facilities']

# facility counts
fig, axs = plt.subplots(2, 2, figsize = (12, 8))
panels = {(0,0):'Midwest', (1,0):'Northeast', (0,1):'West', (1,1):'South'}
for key, value in panels.items():
    data = df.loc[df['Region'] == value]
    ax1 = axs[key]
    ax1.set_title(f'{value}')
    ax1.set_xlabel('time')
    ax1.set_ylabel('facilities', color = 'tab:red')
    ax1.plot('year', 'facilities', data = data, color = 'tab:red')
    ax1.tick_params(axis = 'y', labelcolor = 'tab:red')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('waitlist additions', color = 'tab:blue')
    ax2.plot('year', 'waitlist_additions', data = data, color = 'tab:blue')
    ax2.tick_params(axis = 'y', labelcolor = 'tab:blue')

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Dialysis Facilities and Waitlist Additions by Region', y = 1)
plt.savefig('figures/facilities_waitlist_region_trends.jpg')
plt.show()

# dialysis chain makeup
fig, axs = plt.subplots(2, 2, figsize = (12, 8))
for key, value in panels.items():
    data = df.loc[df['Region'] == value]
    ax1 = axs[key]
    ax1.set_title(f'{value}')
    ax1.set_xlabel('time')
    ax1.set_ylabel("% chain", color = 'tab:red')
    ax1.plot('year', 'pct_chain', data = data, color = 'tab:red')
    ax1.tick_params(axis = 'y', labelcolor = 'tab:red')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('waitlist additions', color = 'tab:blue')
    ax2.plot('year', 'waitlist_additions', data = data, color = 'tab:blue')
    ax2.tick_params(axis = 'y', labelcolor = 'tab:blue')

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Proportion Dialysis Chains and Waitlist Additions by Region',  y = 1)
plt.savefig('figures/pctchain_waitlist_region_trends.jpg')
plt.show()

# dialysis chain makeup (pct big2)
fig, axs = plt.subplots(2, 2, figsize = (12, 8))
for key, value in panels.items():
    data = df.loc[df['Region'] == value]
    ax1 = axs[key]
    ax1.set_title(f'{value}')
    ax1.set_xlabel('time')
    ax1.set_ylabel("% Davita/Fresenius", color = 'tab:red')
    ax1.plot('year', 'pct_big2', data = data, color = 'tab:red')
    ax1.tick_params(axis = 'y', labelcolor = 'tab:red')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('waitlist additions', color = 'tab:blue')
    ax2.plot('year', 'waitlist_additions', data = data, color = 'tab:blue')
    ax2.tick_params(axis = 'y', labelcolor = 'tab:blue')

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Proportion Davita/Fresenius and Waitlist Additions by Region',  y = 1)
plt.savefig('figures/pctdavfre_waitlist_region_trends.jpg')
plt.show()

### STATE LEVEL ###
# look at states in the upper quartile of ckd prevalence
ckd = pd.read_pickle('data/intermed/ckd_county.pkl')

ckd['ckd_high'] = np.where(ckd['KIDNEY_AdjPrev'] > (ckd['KIDNEY_AdjPrev'].quantile(0.75)), 1, 0)
ckd_high = ckd.groupby('StateAbbr')['ckd_high'].mean()
states = ckd_high.loc[ckd_high > 0.5].index.values

dialysis_state['pct_chain'] = dialysis_state['chain'] / dialysis_state['facilities']
dialysis_state['pct_big2'] = (dialysis_state['davita'] + dialysis_state['fresenius']) / dialysis_state['facilities']

# facility counts
fig, axs = plt.subplots(3, 2, figsize = (12, 8))
panels = {(0,0):f'{states[0]}', (1,0):f'{states[1]}', (2, 0):f'{states[2]}', (0,1):f'{states[3]}', (1,1):f'{states[4]}', (2, 1):f'{states[5]}'}
for key, value in panels.items():
    data = dialysis_state.loc[dialysis_state['state'] == value]
    ax1 = axs[key]
    ax1.set_title(f'{value}')
    ax1.set_xlabel('time')
    ax1.set_ylabel("facilities", color = 'tab:red')
    ax1.plot('year', 'facilities', data = data, color = 'tab:red')
    ax1.tick_params(axis = 'y', labelcolor = 'tab:red')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('waitlist additions', color = 'tab:blue')
    ax2.plot('year', 'waitlist_additions', data = data, color = 'tab:blue')
    ax2.tick_params(axis = 'y', labelcolor = 'tab:blue')

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Dialysis Facilities and Waitlist Additions by State', y = 1)
plt.savefig('figures/facilities_waitlist_state_trends.jpg')
plt.show()

# dialysis chain makeup
fig, axs = plt.subplots(3, 2, figsize = (12, 8))
for key, value in panels.items():
    data = dialysis_state.loc[dialysis_state['state'] == value]
    ax1 = axs[key]
    ax1.set_title(f'{value}')
    ax1.set_xlabel('time')
    ax1.set_ylabel("% chain", color = 'tab:red')
    ax1.plot('year', 'pct_chain', data = data, color = 'tab:red')
    ax1.tick_params(axis = 'y', labelcolor = 'tab:red')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('waitlist additions', color = 'tab:blue')
    ax2.plot('year', 'waitlist_additions', data = data, color = 'tab:blue')
    ax2.tick_params(axis = 'y', labelcolor = 'tab:blue')

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Proportion Dialysis Chains and Waitlist Additions by Region',  y = 1)
plt.savefig('figures/pctchain_waitlist_state_trends.jpg')
plt.show()

# dialysis chain makeup (pct big2)
fig, axs = plt.subplots(3, 2, figsize = (12, 8))
for key, value in panels.items():
    data = dialysis_state.loc[dialysis_state['state'] == value]
    ax1 = axs[key]
    ax1.set_title(f'{value}')
    ax1.set_xlabel('time')
    ax1.set_ylabel("% Davita/Fresenius", color = 'tab:red')
    ax1.plot('year', 'pct_big2', data = data, color = 'tab:red')
    ax1.tick_params(axis = 'y', labelcolor = 'tab:red')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('waitlist additions', color = 'tab:blue')
    ax2.plot('year', 'waitlist_additions', data = data, color = 'tab:blue')
    ax2.tick_params(axis = 'y', labelcolor = 'tab:blue')

plt.subplots_adjust(top = 0.85)
fig.tight_layout()
fig.suptitle('Proportion Davita/Fresenius and Waitlist Additions by Region',  y = 1)
plt.savefig('figures/pctdavfre_waitlist_state_trends.jpg')
plt.show()