# TCVD_PRA1

Repository for the PRA1 of the subject "Tipología y ciclo de vida de los datos" of the UOC Master's degree in Data Science

## Contributors

Adrian Läufer Nicolás

Aleksandar Rasevic Lukic

## Description

The file structure in this repo can be described as follows:

* **/source/**: directory that contains all of the relevant code for the web scraping exercise. Contains the files:
  * **fotocasa_scraping.py**: library with code and functions to scrape data from the website Fotocasa.
  * **idealista_scraping.py**: library with code and functions to scrape data from the website Idealista.
  * **main.py**: script used as the central point of execution, accessing the aforementioned libraries.
  * **requirements.txt**: file containing the necessary external libraries to execute toe code above.
* **/dataset/**: directory that contains all of the relevant data extracted as a result of the execution of the files in the **/source/** repo.
  * **output_fotocasa.csv**: csv file containing the results of the execution of the library **fotcasa_scraping.py**'s main method.
  * **output_idealista.csv**: csv file containing the results of the execution of the library **idealista_scraping.py**'s main method.
  * **output_concat.csv**: csv file containing the concatenation of both files above, resulting from the execution of **main.py**.
* **PRACTICA1_arasevic_adrianlaufer.pdf**: pdf file containing the answers to the problems listed in PRA1's statement.

## Zenodo DOI

10.5281/zenodo.7861754
