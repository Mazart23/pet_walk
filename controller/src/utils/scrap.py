

import logging
import time 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


log = logging.Logger('### SCRAPER ###')

URL = "https://www.goodlood.com/loodspoty"


def fetch_loodspots_krakow() -> list:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    wrapper = soup.find("div", id="loodspot-collection-list-wrapper")
    if not wrapper:
        raise ValueError("Cannot find div z id 'loodspot-collection-list-wrapper'")

    collection_list = wrapper.find("div", attrs={ "role": "list"})
    if not collection_list:
        raise ValueError("Cannot find div with class 'collection-list-2 w-dyn-items'")

    items = collection_list.find_all("div", class_="loodspot-item w-dyn-item")

    loodspots = []
    for item in items:
        city = item.find("p", attrs={"fs-cmsfilter-field": "Miasto"})
        if city.get_text(strip=True).lower() not in {'kraków', 'krakow', 'cracow'}:
            continue
        name = item.find("h3", attrs={"px-map": "name"})
        address = item.find("p", class_="paragraph-1")
        longitude = item.find("p", attrs={"px-map": "longitude"})
        latitude = item.find("p", attrs={"px-map": "latitude"})

        if not (name and address and longitude and latitude):
            continue

        loodspots.append({
            "name": name.get_text(strip=True),
            "address": address.get_text(strip=True),
            "lng": float(longitude.get_text(strip=True)),
            "lat": float(latitude.get_text(strip=True)),
        })

    return loodspots