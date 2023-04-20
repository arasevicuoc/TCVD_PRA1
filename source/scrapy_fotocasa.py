# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 09:50:05 2023

@author: adria
"""

import csv
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import re

# Set up the web driver
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
#options = webdriver.ChromeOptions()
#options.add_argument("window-size=1280,800") # Cambiar el tamaño de la ventana del navegador
#driver = webdriver.Chrome(options=options)
driver.get("https://www.fotocasa.es/es/comprar/viviendas/vilanova-i-la-geltru/todas-las-zonas/l")



names = []
prices = []
rooms = []
squaremeters = []
planta = []
links = []
garage = []
elevator = []
CardPackType = []
pagina=1

while True:
    # Scroll down to the bottom of the page and extract the events
    for i in range(20):
        ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(
            Keys.PAGE_DOWN).perform()
        time.sleep(4)


    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # Get the events on the current page
    elementsPremiumg = soup.find_all("article", class_="re-CardPackPremium")
    elementsAdvance = soup.find_all("article", class_="re-CardPackAdvance")
    elementsBasic = soup.find_all("article", class_="re-CardPackBasic")
    elements = elementsPremiumg + elementsAdvance + elementsBasic
    
    for item in elements:
        name = item.find('span', {'class': 're-CardTitle'})
        names.append(name.text.strip())
        
        
        price = item.find('span', {'class': 're-CardPrice'})
        if prices is None:
            pass
        else:
            prices.append(price.text.strip())
        
        link = item.find('a', {'class': 're-CardPackPremium-info-container'})
        if link is None:
            link = item.find('a', {'class': 're-CardPackAdvance-info-container'})
            if link is None:
                link = item.find('a', {'class': 're-CardPackBasic-info-container'})
                if link is None:
                    links.append('-')
                else:
                    links.append("https://www.fotocasa.es"+link.get('href'))
                    CardPackType.append('CardPackBasic')
            else:
                links.append("https://www.fotocasa.es"+link.get('href'))
                CardPackType.append('CardPackAdvance')
        else:
            links.append("https://www.fotocasa.es"+link.get('href'))
            CardPackType.append('CardPackPremium')
        
        numrooms = item.find('span', {'class': 're-CardFeaturesWithIcons-feature-icon re-CardFeaturesWithIcons-feature-icon--rooms'})
        if numrooms is None:
            rooms.append('-')
        else:
            rooms.append(numrooms.text.strip())
            
        sqm = item.find('span', {'class': 're-CardFeaturesWithIcons-feature-icon re-CardFeaturesWithIcons-feature-icon--surface'})
        if sqm is None:
            squaremeters.append('-')
        else:
            squaremeters.append(sqm.text.strip())
        
        numplanta = item.find('span', {'class': 're-CardFeaturesWithIcons-feature-icon re-CardFeaturesWithIcons-feature-icon--floor'})
        if numplanta is None:
            planta.append('-')
        else:
            planta.append(numplanta.text.strip())
            
        ascensor = item.find('span', {'class': 're-CardFeaturesWithIcons-feature-icon re-CardFeaturesWithIcons-feature-icon--elevator'})
        if ascensor is None:
            elevator.append('No')
        else:
            elevator.append('Si')
        
        parking = item.find('span', {'class': 're-CardFeaturesWithIcons-feature-icon re-CardFeaturesWithIcons-feature-icon--parking'})
        if parking is None:
            garage.append('No')
        else:
            garage.append('Si')
    
    elementsMinimal = soup.find_all("article", class_="re-CardPackMinimal")
    for item in elementsMinimal:
        name = item.find('span', {'class': 're-CardTitle'})
        names.append(name.text.strip())
            
            
        price = item.find('span', {'class': 're-CardPrice'})
        if prices is None:
            prices.append('-')
        else:
            prices.append(price.text.strip())
        
        link = item.find('a', {'class': 're-CardPackMinimal-info-container'})
        if link is None:
            link.append('-')
        else:
            links.append("https://www.fotocasa.es"+link.get('href'))
            CardPackType.append('CardPackMinimal')
        
        details =item.find_all('li', {'class': 're-CardFeatures-feature'})
        details_list = []
        
        for i in range(len(details)):
            details_list.append(details[i].text.strip())
        
        pattern_sqm = r'.*m²'
        pattern_rooms = r'.*habs.*'
        pattern_planta = r'.*Planta'        
        pattern_parking = r'Parking'        
        pattern_ascensor = r'Ascensor'        
        
        if len(details_list) ==0:
            print(item)
            squaremeters.append('-')
            rooms.append('-')
            planta.append('-')
            garage.append('-')
            elevator.append('-')
        else:
            a = b = c = d = e = 0
            for i in details_list:
                if re.search(pattern_sqm, i):
                    squaremeters.append(i)
                    a = 1
                if re.search(pattern_rooms, i):
                    rooms.append(i)
                    b = 1
                if re.search(pattern_planta, i):
                    planta.append(i)
                    c = 1
                if re.search(pattern_parking, i):
                    garage.append('Si')          
                    d = 1
                if re.search(pattern_ascensor, i):
                    elevator.append('Si')
                    e = 1
            if a == 0:
                squaremeters.append('-')
            if b == 0:
                rooms.append('-')
            if c == 0:
                planta.append('-')
            if d == 0:
                garage.append('No')
            if e == 0:
                elevator.append('No')
                      
    # Check if there is a next page
    # next_link = soup.find_all("span", class_="sui-AtomButton-rightIcon")
    # if len(next_link)==0:
    #    driver.quit()
    #    break
    if pagina > 37:
        driver.quit()
        break
    else:
        pagina=pagina+1
        driver.quit()
        time.sleep(4)
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get("https://www.fotocasa.es/es/comprar/viviendas/vilanova-i-la-geltru/todas-las-zonas/l"+"/"+str(pagina))

# Define the filename of the CSV file
filename = 'output_fotocasa.csv'
        
# Open the CSV file in write mode
with open(filename, mode='w', newline='') as file:

    # Create a CSV writer object
    writer = csv.writer(file)

    # Write the headers for each column
    writer.writerow(['Name', 'Price', 'Rooms', 'M2','Parking','Link','Fuente','Elevator','Floor','Type'])

    # Write each row of data to the CSV file
    for i in range(len(prices)):
        writer.writerow([names[i], prices[i], rooms[i], squaremeters[i], garage[i], links[i], "fotocasa", elevator[i], planta[i], CardPackType[i]])
