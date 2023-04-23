# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 09:50:05 2023

@authors:
Adrian Läufer Nicolás
Aleksandar Rasevic Lukic
"""
import csv
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import re
import pandas as pd

info_card_types = [
    'Premium', 'Advance', 'Basic', 'Minimal'
]

minimal_features = {
    'm²': 'surface',
    'habs': 'rooms',
    'Planta': 'floor',
    'Parking': 'parking',
    'Ascensor': 'elevator',
    'Terraza': 'terrace',
    'Aire': 'air_conditioner',
    'Calefacción': 'heating'
}

keys = "Vilanova i la Geltrú"

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


def _initial_search(driver: webdriver.Chrome, keys: str) -> webdriver.Chrome.find_element:
    """
    In the first page we need to accept cookies, select between buy/rental and
    input a search area. We compress these operations and return the xpath
    for the cookies element, which will be pushed in subsequent tries.

    :param driver: an initialized webdriver.Chrome instance
    :param keys: the area to search
    :return: the 'accept cookies' button xpath
    """
    time.sleep(2)
    cookies = driver.find_element('xpath', './/div[@class="sui-TcfFirstLayer-buttons"]//button[@class="sui-AtomButton sui-AtomButton--primary sui-AtomButton--solid sui-AtomButton--center "]')
    cookies.click()

    time.sleep(2)
    alquiler = driver.find_element('xpath', './/div[@class="re-HomeSearchSelector-item re-HomeSearchSelector-item--buy"]')
    alquiler.click()

    time.sleep(2)
    filtro = driver.find_element('xpath', './/div[@class="sui-AtomInput--withIcon sui-AtomInput--withIcon--right"]//input[@class="sui-AtomInput-input sui-AtomInput-input-size-m"]')
    filtro.send_keys(keys)
    filtro.send_keys(Keys.RETURN)

    return cookies

def _scroll_page_down(iterations: int, delay: int, driver: webdriver.Chrome):
    """
    Scroll down the page with an iterations number of times with a delay number
    of seconds of wait. Usually, 25 iterations is enough to get to the bottom
    of the page.

    :param iterations: number of 'down' button presses to be executed through JS
    :param delay: number of seconds to wait between presses
    :param driver: an initialized webdriver.Chrome instance
    :return:
    """
    for i in range(iterations):
        ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(
            Keys.PAGE_DOWN).perform()
        time.sleep(delay)


def _card_type_is_minimal_info(info_card: BeautifulSoup) -> dict:
    """
    When the CardPack is of type Minimal, the features are not distinguished
    in name of the li class attribute, but appear under the generic name
    'feature'. After manual analysis, the keys discovered appear in the global
    array 'minimal_features', which we use as keys of the returned feature line.

    :param info_card: a CardPack object of type Minimal
    :return: a dictionary of real estate features
    """
    feature_line = dict([])
    house_features = info_card.find_all('li',
                                        {'class': 're-CardFeatures-feature'})
    for house_feature in house_features:
        for considered_house_feature in minimal_features.keys():
            if considered_house_feature in house_feature.get_text():
                feature_line[minimal_features[
                    considered_house_feature]] = house_feature.get_text()
    return feature_line


def _card_type_is_not_minimal_info(info_card: BeautifulSoup) -> dict:
    """
    If the CardPack object is not of type Minimal, the features appear in the
    name of the span, so there's no need to maintain a global list of keys.
    We can extract both the name and the value using regexp.

    :param info_card: a CardPack object of type Basic, Advanced or Premium
    :return: a dictionary of real estate features
    """
    feature_line = dict([])
    # There are two possible 'ul' objects where the info can be found, determined
    # after manual inspection. The first one is the most common, with some exceptions
    # appearing as the second one. Were there to exist a third, undetermined
    # type, return an empty line.
    house_features = info_card.find('ul', {
        'class': 're-CardFeaturesWithIcons-wrapper re-CardFeaturesWithIcons-wrapper--isTwoLines'})
    if house_features == None:
        house_features = info_card.find('ul', {
            'class': 're-CardFeaturesWithIcons-wrapper'})
    if house_features == None:
        return dict([])
    for house_feature in house_features.find_all('span'):
        house_feature_value = house_feature.get_text()
        if len(house_feature['class']) > 1:
            house_feature_name = re.search(
                're-CardFeaturesWithIcons-feature-icon--(.*)',
                house_feature['class'][1])
            if house_feature_name is not None:
                feature_line[house_feature_name.group(1)] = house_feature_value
            elif len(house_feature['class']) == 1:
                feature_line['extras'] = house_feature_value
    return feature_line


def _get_generic_information(info_card: BeautifulSoup, info_card_type: str) -> dict:
    """
    Whether the CardPack object is Minimal, Basic, Advanced or Premium, a few
    fields are generic enough to be found through all cards: title, link,
    price and CardType for possible debugging purposes.

    :param info_card: a BeautifulSoup div containing all info for the property
    :param info_card_type: can be one of Minimal, Basic, Advanced or Premium
    :return: a dictionary with the generic information of the card
    """
    title = info_card.find('a', {'class': f'{info_card_type}-container'})[
        'title']
    link = info_card.find('a', {'class': f'{info_card_type}-container'})[
        'href']
    price = info_card.find('span', {'class': 're-CardPrice'})
    return {'title': title, 'link': link, 'info_card_type': info_card_type,
            'price': price.get_text()}

def _get_next_page(soup: BeautifulSoup, base_url: str, current_page: str,
                   page_index: int, page_index_limit: int = 20) -> str:
    """
    Get either the URL for the next page to be scraped, or None if several
    conditions take place:
    * If the link to the next page is identical to the current page, we are at
      the last page and finish the scraping.
    * If we have already scraped page_index_limit pages, we finish the scraping.

    :param soup: the BeautifulSoup object containing the info to be scraped
    :param base_url: the base URL of the website, to which we append the next
      page link
    :param current_page: the URL of the current page in the scraping
    :param page_index: an integer representing the amount of pages scraped
    :param page_index_limit: an integer representing the max amount of pages
      to be scraped
    :return: URL to the next page or None
    """
    next_page_links = soup.find_all('a', {'shape': 'rounded'})
    next_page_link = next_page_links[-1]
    next_page = base_url[:-4] + next_page_link['href']
    if next_page_link == current_page or page_index == page_index_limit:
        return None
    else:
        return next_page

def _get_unique_keys(all_info: dict) -> list:
    """
    The methods used through this project yield dictionaries of uneven length,
    as we scrape all of the data available in the CardPack objects. This yields
    uneven dictionaries, which might be problematic to translate to relational
    formats such as dataframes or csv files.

    This method extracts a list of unique keys to ease the relational storing.

    :param all_info: a dictionary containing all of the information scraped
    :return: a list containing a list of unique keys found while scraping
    """
    unique_fields = []
    for page in all_info.keys():
        for feature_line in all_info[page]:
            unique_fields.extend(list(feature_line.keys()))
    return list(set(unique_fields))

def _dump_to_csv(all_info: dict, csv_name: str='output_fotocasa.csv'):
    """
    Store the all_info dictionary at csv_name path as a csv file.

    :param all_info: a dictionary containing all of the scraped info
    :param csv_name: the path where to store the .csv file
    """
    with open(csv_name, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=_get_unique_keys(all_info), delimiter=',')
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
    unique_fields = _get_unique_keys(all_info)
    df = pd.DataFrame()
    for page in all_info.keys():
        df = df.append(pd.DataFrame.from_records(all_info[page], columns=unique_fields))
    return df

def scrape_fotocasa(base_url: str='https://www.fotocasa.es/es/',
                    area: str="Vilanova i la Geltrú",
                    csv_name: str=f"./data/fotocasa.csv",
                    page_index_limit: int=20):
    """
    Main method to be called by external libraries. Scrapes the portal Fotocasa
    using as a base endpoint 'base_url' and searching within the area 'area'.

    :param base_url: self-explanatory
    :param area: self-explanatory. Must abide by Fotocasa's naming convention,
      which must be explored before executing the script
    :param csv_name: string representing the name of the stored CSV
    :param page_index_limit: int representing the maximum amount of pages
      to be scraped, unless pagelimit is reached first
    :return: a pandas DataFrame and stores a CSV with the same information as
      a side-effect
    """
    driver = _initialize_driver()
    driver.get(base_url)
    cookies = _initial_search(driver, keys=area)
    current_page = str(driver.current_url)

    page_index = 1
    all_pages_traversed = False
    all_info = dict([])

    while not all_pages_traversed:
        _scroll_page_down(25, 2, driver)
        html_text = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(html_text, features="html.parser")

        info_cards = []
        for info_card_type in info_card_types:
            # There's 4 possible CardPack classes: investigate them all
            info_cards.extend(soup.find_all('div', {'class': f're-CardPack{info_card_type}-info'}))
            feature_lines = []
            for info_card in info_cards:
                feature_line = dict([])
                if info_card.has_attr('class'):
                    info_card_type = info_card['class'][0]
                    feature_line.update(_get_generic_information(info_card, info_card_type))
                    # The scraping method differs whether it's a Minimal or not
                    if info_card_type in ['re-CardPackPremium-info', 're-CardPackAdvance-info', 're-CardPackBasic-info']:
                        feature_line.update(_card_type_is_not_minimal_info(info_card))
                    elif info_card_type == 're-CardPackMinimal-info':
                        feature_line.update(_card_type_is_minimal_info(info_card))
                    feature_lines.append(feature_line)

        all_info[f'page_{page_index}'] = feature_lines
        next_page = _get_next_page(soup, base_url, current_page,
                                   page_index, page_index_limit)

        # Reinstantiante the driver to continue the scraping
        if next_page is not None:
            driver.quit()
            time.sleep(4)
            driver = _initialize_driver()
            cookies.click()
            driver.get(next_page)
        else:
            all_pages_traversed = True
        page_index += 1

    driver.quit()
    _dump_to_csv(all_info, csv_name)
    return _dump_to_dataframe(all_info)

if __name__ == '__main__':
    scrape_fotocasa()

