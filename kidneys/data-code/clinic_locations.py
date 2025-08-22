import pandas as pd
import geopandas as gpd
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm
tqdm.pandas()

dialysis = pd.read_csv('data/input/DFC_FACILITY.csv', dtype = {
    'Address Line 1': str,
    'Address Line 2': str,
    'City/Town': str,
    'State': str,
    'ZIP Code': str
})

dialysis['address'] = dialysis['Address Line 1'].str.cat(
    [dialysis['Address Line 2'], dialysis['City/Town'], dialysis['State'], dialysis['ZIP Code']], sep=',', na_rep = '')

geolocator = ArcGIS(user_agent="clinic_locator", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=5)
dialysis['location'] = dialysis['address'].progress_apply(geocode)
print('geocoding done!')
dialysis['longitude'] = dialysis['location'].apply(lambda loc: loc.longitude if loc else None)
dialysis['latitude'] = dialysis['location'].apply(lambda loc: loc.latitude if loc else None)
print(dialysis['location'].isna().sum(), "locations could not be geocoded.")

dialysis.to_csv('data/input/dialysis_locations.csv', index=False)
dialysis = gpd.GeoDataFrame(dialysis, geometry=gpd.points_from_xy(dialysis.longitude, dialysis.latitude))
dialysis.to_file('data/input/dialysis_locations.geojson', driver='GeoJSON')