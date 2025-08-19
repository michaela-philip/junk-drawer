import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def scrape_locations(url):
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
    transplant_centers = pd.DataFrame(transplant_centers, columns=['name', 'location'])
    print('scraping done!')
    return transplant_centers

transplant_centers = scrape_locations('https://optn.transplant.hrsa.gov/about/search-membership/')

transplant_centers[['abbrev', 'name']] = transplant_centers['name'].str.split(' - ', n = 1, expand = True)
transplant_centers['address'] = transplant_centers['name'].str.cat(transplant_centers['location'], sep=', ', na_rep = '')

geolocator = Nominatim(user_agent="clinic_locator", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=5)
locations = transplant_centers['address'].apply(geocode)

transplant_centers['longitude'] = locations.apply(lambda loc: loc.longitude if loc else None)
transplant_centers['latitude'] = locations.apply(lambda loc: loc.latitude if loc else None)
transplant_centers.to_csv('data/input/transplant_locations.csv', index = False)

print(transplant_centers['longitude'].isna().sum(), "locations could not be geocoded.")

transplant_centers = gpd.GeoDataFrame(transplant_centers, geometry=gpd.points_from_xy(transplant_centers.longitude, transplant_centers.latitude))
transplant_centers.to_file('data/input/transplant_locations.geojson', driver='GeoJSON') 
print(transplant_centers.info())