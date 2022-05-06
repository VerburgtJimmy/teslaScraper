import json
import pprint
import time
import threading
import re
import pandas as pd

from datetime import datetime

from bs4 import BeautifulSoup
from numpy import append
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

import ctypes  # An included library with Python install.

html = None

f = open('countries.json')
urls = json.load(f)

results_container_selector = 'div.results-container.results-container--grid.results-container--has-results'
delay = 10  # seconds

data = []
cars = []



for city in urls:
    for model in city['urls']:

        try:
            print(model)
            print(datetime.now().strftime("%H:%M:%S") + " Searching Tesla's website in " + city['country'])
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            browser.get(model)

            # wait for results to be displayed
            WebDriverWait(browser, delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, results_container_selector))
            )

        except TimeoutException:
            print('Loading took too much time!')
        else:
            html = browser.page_source
        finally:
            browser.quit()

        if html:
            soup = BeautifulSoup(html, 'lxml')

            results = soup.find(id="iso-container")

            teslas = results.find_all("article", class_="result")

            for tesla in teslas:
                car = {}
                # Get all values from page and add to data
                car['price'] = tesla.find("span", class_="result-purchase-price").text
                car['colour'] = tesla.find("ul", class_="result-regular-features").select("li")[0].get_text(strip=True)
                car['type'] = tesla.find("div", class_="result-basic-info").find("h3", recursive=False).text
                


                car['trim'] = tesla.select("div > div", class_="result-basic-info")[0].get_text(strip=True)
                car['mileage'] = tesla.select("div > div", class_="result-basic-info")[1].get_text(strip=True)
                car['location'] = tesla.select("div > div", class_="result-basic-info")[2].get_text(strip=True)
                car['wheels'] = tesla.find("ul", class_="result-regular-features").select("li")[1].get_text(strip=True)
                car['interior'] = tesla.find("ul", class_="result-regular-features").select("li")[2].get_text(strip=True)

                cars = append(cars, car)
    
    countryData = {}
    countryData['country'] = city['country']
    countryData['cars'] = cars
    data = append(data, countryData)
    cars = []
    
    time.sleep(30) # seconds


pd.Series(data).to_json('data.json', orient='split')
# jsonString = json.dumps(data)
# jsonFile = open("data.json", "w")
# jsonFile.write(jsonString)
# jsonFile.close()