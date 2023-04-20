# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 09:50:05 2023

@authors:   
Aleksandar Rasevic Lukic
Adrian Läufer Nicolás
            
"""
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Set up the web driver Google Chrome
options = webdriver.ChromeOptions()
options.add_argument("window-size=1280,800") # Cambiar el tamaño de la ventana del navegador
driver = webdriver.Chrome(options=options)

# Set up the web driver Firefox
# driver = webdriver.Firefox()
driver.get("https://www.idealista.com/buscar/venta-viviendas/vilanova-i-la-geltru-barcelona/Vilanova_i_la_Geltru/")

# Scroll down to the bottom of the page and extract the events
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
events_name = []
events_location = []

# Create the variables where we will store the information
names = []
prices = []
rooms = []
squaremeters = []
planta = []
links = []
garage = []

time.sleep(10)

while True:
    # Get the events on the current page
    elements = soup.find_all('div', {'class': 'item-info-container'})
    for item in elements:
        # Save the name of the element
        name = item.find('a', {'class': 'item-link'}).text.strip()
        names.append(name)
        
        # Save the price of the element        
        price = item.find('span', {'class': 'item-price h2-simulated'}).text.strip()
        prices.append(price)
        
        # Save the link of the element
        link = item.find('a', {'class': 'item-link'}).get('href')
        links.append("https://www.idealista.com"+link)
        
        # Save the number of rooms, the squaremeters and the number of floor of the element
        detail = item.find_all('span', {'class': 'item-detail'})
        if len(detail) == 0:                
            rooms.append('-')
            squaremeters.append('-')
            planta.append('-')
        elif len(detail) == 1:
            rooms.append(detail[0].text.strip())
            squaremeters.append('-')
            planta.append('-')
        elif len(detail) == 2:
            rooms.append(detail[0].text.strip())
            squaremeters.append(detail[1].text.strip())
            planta.append('-')
        else:
            rooms.append(detail[0].text.strip())
            squaremeters.append(detail[1].text.strip())
            planta.append(detail[2].text.strip())

        # Save if the flat has parking
        parking = item.find('span', {'class': 'item-parking'})
        if parking is None:
            garage.append('No')
        else:
            garage.append('Si')
        
    # Check if there is a next page
    next_link = soup.find('a', class_='icon-arrow-right-after')
    time.sleep(15)
    if next_link is None:
        print("Break")
        break
    else:
        # Click on the pagination link to go to the next page 
        element = driver.find_element(By.CLASS_NAME, 'icon-arrow-right-after')
        driver.execute_script("arguments[0].click();", element)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
   
# Close the web driver
driver.quit()

# Define the filename of the CSV file where we want to store the output
filename = 'output_idealista_Vilanova.csv'

# Open the CSV file in write mode
with open(filename, mode='w', newline='') as file:

    # Create a CSV writer object
    writer = csv.writer(file)

    # Write the headers for each column
    writer.writerow(['Name', 'Price', 'Rooms', 'M2', 'Parking', 'Link', 'Fuente'])

    # Write each row of data to the CSV file
    for i in range(len(prices)):
        writer.writerow([names[i], prices[i], rooms[i], squaremeters[i], 
                         garage[i], links[i], "idealista"])