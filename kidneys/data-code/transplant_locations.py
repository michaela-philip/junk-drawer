import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import geopandas as gpd
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
from tqdm import tqdm
tqdm.pandas()

def scrape_locations_optn(url):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # choose to search for transplant hospitals by organ
    membertype = wait.until(EC.element_to_be_clickable((By.NAME, 'memberType')))
    membertype.click()
    membertype.find_element(By.XPATH, './option[@value="Transplant Hospitals By Organ"]').click()
    time.sleep(2)

    # click on "Go" button
    go = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[img[@alt="GO"]]')))
    go.click()
    time.sleep(2)

    # select Kidneys, use second "Go" button
    organtype = wait.until(EC.element_to_be_clickable((By.NAME, 'organType')))
    organtype.click()
    organtype.find_element(By.XPATH, './option[@value="DKI"]').click()
    time.sleep(2)

    orgango = wait.until(EC.element_to_be_clickable((By.ID, 'organGo')))
    orgango.click()
    time.sleep(2)

    # default is 'All' for member status, only need ot click third "Go" button
    memberstatusgo = wait.until(EC.element_to_be_clickable((By.ID, 'memberStatusGo')))
    memberstatusgo.click()
    time.sleep(2)

    # choose all regions
    region = wait.until(EC.element_to_be_clickable((By.NAME, 'region')))
    region.click()
    region.find_element(By.XPATH, './option[@value="0"]').click()
    time.sleep(2)

    regiongo = wait.until(EC.element_to_be_clickable((By.ID, 'imgTop')))
    regiongo.click()
    time.sleep(2)

    transplant_centers = []

    table = driver.find_element(By.CLASS_NAME, 'listTable')
    for row in table.find_elements(By.TAG_NAME, 'tr')[1:]:  # Skip header row
        cells = row.find_elements(By.TAG_NAME, 'td')
        name = cells[0].text
        location = cells[1].text
        transplant_centers.append((name, location))

    driver.quit()
    df = pd.DataFrame(transplant_centers, columns=['name', 'location'])
    print('scraping done!')
    df.to_csv('data/input/transplant_centers_optn.csv', index = False)
    return df


def scrape_locations_srtr(url):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    transplant_centers = []
    while True:
        # identify list of transplant centers
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.searchResults.vr_2n')))
        lis = table.find_elements(By.CLASS_NAME, 'searchResults-item')

        for li in lis:
            name = li.find_element(By.CSS_SELECTOR, 'h5.hdg.hdg_h5').text
            location = li.find_element(By.CLASS_NAME, 'mix-text_weightBold').text
            transplant_centers.append((name, location))
        
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'next')))
            next_button.click()
            print('next page')
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            break

    driver.quit()

    df = pd.DataFrame(transplant_centers, columns=['name', 'location'])
    print('scraping done!')
    df.to_csv('data/input/transplant_centers_srtr.csv', index = False)
    return df
    

def geocode_centers(df):
    geolocator = ArcGIS(user_agent="clinic_locator", timeout=10)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=5)
    locations = df['address'].progress_apply(geocode)

    df['longitude'] = locations.apply(lambda loc: loc.longitude if loc else None)
    df['latitude'] = locations.apply(lambda loc: loc.latitude if loc else None)
    print(df['longitude'].isna().sum(), "locations could not be geocoded.")

    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
    df.to_csv('data/input/transplant_locations.csv', index=False)
    df.to_file('data/input/transplant_locations.geojson', driver='GeoJSON')
    return df

##########################################################################################################

if not os.path.exists('data/input/transplant_centers_optn.csv'):
    transplant_centers_optn = scrape_locations_optn('https://optn.transplant.hrsa.gov/about/search-membership/')
else:
    transplant_centers_optn = pd.read_csv('data/input/transplant_centers_optn.csv')
if not os.path.exists('data/input/transplant_centers_srtr.csv'):
    transplant_centers_srtr = scrape_locations_srtr('https://www.srtr.org/transplant-centers/?organ=kidney')
else:
    transplant_centers_srtr = pd.read_csv('data/input/transplant_centers_srtr.csv')

transplant_centers_optn[['abbrev', 'name']] = transplant_centers_optn['name'].str.split(' - ', n = 1, expand = True)

transplant_centers = pd.merge(transplant_centers_optn, transplant_centers_srtr, on = ['name', 'location'], how = 'outer')
transplant_centers['address'] = transplant_centers['name'].str.cat(transplant_centers['location'], sep=', ', na_rep = '')

transplant_centers = geocode_centers(transplant_centers)
print(transplant_centers.info())