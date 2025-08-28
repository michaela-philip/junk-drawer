import pandas as pd
import geopandas as gpd
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
tqdm.pandas()

# standardize column names to make a super simple panel
dfc_columns_standard = {
    'City/Town': 'City',
    'County/Parish':'County',
    'CMS Certification Number (CCN)': 'Provider Number',
    'NETWORK': 'Network',
    'Chain owned': 'Chain Owned',
    'ZIP Code': 'Zip'
}
dfc_columns = ['Provider Number', 'Network', 'Facility Name', 
                    'Address Line 1', 'Address Line 2',  'City', 'State', 
                   'Zip', 'County', 'Chain Owned', 'Chain Organization']

dfc_2018 = pd.read_csv('data/input/dfc_cms/DFC_FACILITY_2018.csv', dtype = str).rename(columns = dfc_columns_standard).loc[:, dfc_columns].assign(year = 2018)
dfc_2019 = pd.read_csv('data/input/dfc_cms/DFC_FACILITY_2019.csv', dtype = str).rename(columns = dfc_columns_standard).loc[:, dfc_columns].assign(year = 2019)
dfc_2020 = pd.read_csv('data/input/dfc_cms/DFC_FACILITY_2020.csv', dtype = str).rename(columns = dfc_columns_standard).loc[:, dfc_columns].assign(year = 2020)
dfc_2021 = pd.read_csv('data/input/dfc_cms/DFC_FACILITY_2021.csv', dtype = str).rename(columns = dfc_columns_standard).loc[:, dfc_columns].assign(year = 2021)
dfc_2022 = pd.read_csv('data/input/dfc_cms/DFC_FACILITY_2022.csv', dtype = str).rename(columns = dfc_columns_standard).loc[:, dfc_columns].assign(year = 2022)
dfc_2023 = pd.read_csv('data/input/dfc_cms/DFC_FACILITY_2023.csv', dtype = str).rename(columns = dfc_columns_standard).loc[:, dfc_columns].assign(year = 2023)
dfc_2024 = pd.read_csv('data/input/dfc_cms/DFC_FACILITY_2024.csv', dtype = str).rename(columns = dfc_columns_standard).loc[:, dfc_columns].assign(year = 2024)
dfc_2025 = pd.read_csv('data/input/dfc_cms/DFC_FACILITY_2025.csv', dtype = str).rename(columns = dfc_columns_standard).loc[:, dfc_columns].assign(year = 2025)
dialysis_panel = pd.concat([dfc_2018, dfc_2019, dfc_2020, dfc_2021, dfc_2022, dfc_2023, dfc_2024, dfc_2025], axis = 0)

dialysis_panel['address'] = dialysis_panel['Address Line 1'].str.cat(
    [dialysis_panel['Address Line 2'], dialysis_panel['City'], dialysis_panel['State'], dialysis_panel['Zip']], sep=',', na_rep = '')

unique_addresses = dialysis_panel.drop_duplicates(subset = ['address'])

geolocator = ArcGIS(user_agent="clinic_locator", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=5)
unique_addresses['location'] = unique_addresses['address'].progress_apply(geocode)
print('geocoding done!')
unique_addresses['longitude'] = unique_addresses['location'].apply(lambda loc: loc.longitude if loc else None)
unique_addresses['latitude'] = unique_addresses['location'].apply(lambda loc: loc.latitude if loc else None)
print(unique_addresses['location'].isna().sum(), "locations could not be geocoded.")

dialysis_panel = dialysis_panel.merge(unique_addresses[['address', 'longitude', 'latitude']], on = ['address'], how = 'left')
dialysis_panel.to_pickle('data/input/dialysis_panel_locations.pkl')