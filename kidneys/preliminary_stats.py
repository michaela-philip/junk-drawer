import pandas as pd
import numpy as np
import geopandas as gpd
import re

dialysis_panel = pd.read_pickle('data/intermed/dialysis_panel_locations.pkl')
counties = pd.read_pickle('data/intermed/counties.pkl')
ckd = pd.read_pickle('data/intermed/ckd_county.pkl')

def export_latex_table(df, columns, caption, label):
    df = df[columns]
    num_cols = df.shape[1]
    col_format = '@{\\extracolsep{\\fill}}l*' + f'{{{num_cols}}}' + '{r}'
    text = df.style.format(precision=2).hide(axis = 'index').to_latex(position_float = 'centering',
                caption=caption, position = 'h', label=label, hrules=True, column_format = col_format)
    text = text.replace('\\begin{tabular}', '\\begin{tabular*}{\\linewidth}').replace('\\end{tabular}', '\\end{tabular*}')
    filename = label.split(':')[-1] + '.tex'
    with open('tables/' + filename, 'w') as f:
        f.write(text)

# dissolve to county level
dialysis_county = dialysis_panel.dissolve(by = ['County', 'year'], aggfunc = 'sum').reset_index()

year_trend = dialysis_county.groupby('year').agg({'chain':'sum', 'davita':'sum', 'fresenius':'sum', 'count':'sum'}).reset_index()
year_trend['pct_chain'] = year_trend['chain'] / year_trend['count']
year_trend['pct_big2'] = (year_trend['davita'] + year_trend['fresenius']) / year_trend['count']
column_dict = {'year':'Year', 'pct_chain':'Percent Chain', 'pct_big2':'Percent Davita or Fresenius'}
year_trend = year_trend.rename(columns = column_dict)
columns = column_dict.values()
export_latex_table(year_trend, columns = columns, caption = 'Trends in Dialysis Ownership', label= 'tab:dialysis_trends')

# look at high ckd counties over time
ckd['ckd_high'] = np.where(ckd['KIDNEY_AdjPrev'] > (ckd['KIDNEY_AdjPrev'].quantile(0.75)), 1, 0)
ckd['CountyName'] = ckd['CountyName'].str.lower()
dialysis_county['County'] = dialysis_county['County'].str.lower()

df = pd.merge(dialysis_county, ckd, left_on = ['State', 'County'], right_on = ['StateAbbr', 'CountyName'], how = 'inner')
df = df[df['ckd_high'] == 1]
high_ckd_trend = df.groupby('year').agg({'chain':'sum', 'davita':'sum', 'fresenius':'sum', 'count':'sum'}).reset_index()
high_ckd_trend['pct_chain'] = high_ckd_trend['chain'] / high_ckd_trend['count']
high_ckd_trend['pct_big2'] = (high_ckd_trend['davita'] + high_ckd_trend['fresenius']) / high_ckd_trend['count']
high_ckd_trend = high_ckd_trend.rename(columns = column_dict)
export_latex_table(high_ckd_trend, columns = columns, caption = 'Trends in Dialysis Ownership (High CKD Counties)', label = 'tab:high_ckd_dialysis_trends')