# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 09:50:05 2023

@authors:
Adrian Läufer Nicolás
Aleksandar Rasevic Lukic
"""
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.idealista.com"

features_to_scrape = [
    'name',
    'price',
    'link',
    'room',
    'squaremeters',
    'floor',
    'parking'
]

def _initialize_driver(executable_path: str=r'chromedriver') -> webdriver.Chrome:
    """
    Basic initialization operations. Useful when restarting the driver while
    traversing the different pages.

    :param executable_path: url where the executable for the Webdriver is found
    :return: a webdriver.Chrome instance
    """
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(executable_path=executable_path, options=options)
    driver.set_window_size(1280, 800)
    return driver


def _get_generic_information(info_container: BeautifulSoup,
                             base_url: str) -> dict:
    """
    Get the name, price and link of a real estate property from the Idealista
    portal. This information is fairly generic for all objects listed.

    :param info_container: a BeautifulSoup object containing the html info to
      scrape
    :param base_url: the base url of the website, used to store the links
      in a more direct fashion
    :return: a dictionary representing the generic information listed above
    """
    name = info_container.find('a', {'class': 'item-link'}).text.strip()
    price = info_container.find('span', {
        'class': 'item-price h2-simulated'}).text.strip()
    link = base_url + info_container.find('a', {'class': 'item-link'}).get(
        'href')
    return {'name': name, 'price': price, 'link': link}


def _get_non_generic_information(info_container: BeautifulSoup) -> dict:
    """
    Get information based on our scraping interests and the stuctural
    restrictions of the scraped website. For our scenario, we're interested
    in the number of rooms, squaremeters, floor and parking.

    :param info_container: BeautifulSoup object holding the information to be
      extract
    :return: a dictionary represeting the non generic information listed
      above
    """
    detail = info_container.find_all('span', {'class': 'item-detail'})
    # depending on the length of the detail object, we find different
    # information available for scraping:
    room = None
    squaremeters = None
    floor = None
    # information shows up in a positional fashion. Longer objects
    # might contain other information we're not currently interested in
    if len(detail) > 0:
        room = detail[0].text.strip()
    if len(detail) > 1:
        squaremeters = detail[1].text.strip()
    if len(detail) > 2:
        floor = detail[2].text.strip()

    # finally, search for parking information
    parking = info_container.find('span', {'class': 'item-parking'})

    return {
        'room': room if room is not None else '-',
        'squaremeters': squaremeters if squaremeters is not None else '-',
        'floor': floor if floor is not None else '-',
        'parking': 'Si' if parking is not None else 'No'
    }

def _dump_to_csv(all_info: dict, csv_name: str='output_idealista.csv'):
    """
    Store the all_info dictionary at csv_name path as a csv file.

    :param all_info: a dictionary containing all of the scraped info
    :param csv_name: the path where to store the .csv file
    """
    with open(csv_name, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=features_to_scrape, delimiter=',')
        w.writeheader()
        for page in all_info.keys():
            for line in all_info[page]:
                w.writerow(line)

def _dump_to_dataframe(all_info: dict):
    """
    Store the all_info dictionary in a pandas DataFrame for further tasks

    :param all_info: a dictionary containing all of the scraped info
    :return: a pandas DataFrame where all_info is reformated
    """
    df = pd.DataFrame()
    for page in all_info.keys():
        df = df.append(pd.DataFrame.from_records(all_info[page], columns=features_to_scrape))
    return df

def scrape_idealista(base_url: str='https://www.idealista.com',
                    csv_name: str=f"./data/idealista.csv",
                    page_index_limit: int=20):
    """
    Main method to be called by external libraries. Scrapes the portal Idealista
    using as a base endpoint 'base_url'; URL construction for Idealista is more
    challenging than it is for Fotocasa. For this project we've decided to
    hardcode the location Vilanova i la Geltrú.

    :param base_url: self-explanatory.
    :param csv_name: a string representing the csv file produced as a
        side-effect of this function.
    :param page_index_limit: an integer representing the max number of pages
        to be traversed for scraping purposes.
    :return: a pd.DataFrame object containing the data scraped
    """
    driver = _initialize_driver()
    driver.get(base_url + "/buscar/venta-viviendas/vilanova-i-la-geltru-barcelona/Vilanova_i_la_Geltru/")

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    all_info = dict([])
    page_index = 1
    time.sleep(10)
    all_pages_traversed = False

    while not all_pages_traversed:
        feature_lines = []
        # Get the events on the current page
        info_containers = soup.find_all('div', {'class': 'item-info-container'})
        for info_container in info_containers:
            feature_line = dict([])
            feature_line.update(_get_generic_information(info_container, base_url))
            feature_line.update(_get_non_generic_information(info_container))
            feature_lines.append(feature_line)
        # Dump the information extracted on the page to the all_info set
        all_info[f'page_{page_index}'] = feature_lines

        # Check if there is a next page.
        next_link = soup.find('a', class_='icon-arrow-right-after')
        time.sleep(15)
        if next_link is None or page_index == page_index_limit:
            all_pages_traversed = True
        else:
            # Click on the pagination link to go to the next page
            element = driver.find_element(By.CLASS_NAME, 'icon-arrow-right-after')
            driver.execute_script("arguments[0].click();", element)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        page_index += 1

    # Close the web driver
    driver.quit()
    _dump_to_csv(all_info, csv_name)
    return _dump_to_dataframe(all_info)

if __name__ == '__main__':
    scrape_idealista()