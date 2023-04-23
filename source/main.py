from unidecode import unidecode
from datetime import datetime

import pandas as pd
import fotocasa_scraping as fts
import idealista_scraping as ids

column_translator = {
    'title': 'Name',
    'price': 'Price',
    'rooms': 'Rooms',
    'link': 'Link',
    'elevator': 'Elevator',
    'floor': 'Floor',
    'info_card_type': 'Type',
    'parking': 'Parking',
    'surface': 'M2'
}

# fotocasa = pd.read_csv('output_fotocasa.csv')
# idealista = pd.read_csv('output_idealista.csv')
# fotocasa_aleks = pd.read_csv('./fotocasa_vilanova_i_geltru_output.csv', encoding='latin-1')
#
# print(f'Original columns on Idealista dataset: {idealista.columns}')
# print(f'Original columns on Fotocasa-Aleks dataset: {fotocasa_aleks.columns}')
# fotocasa.insert(loc=fotocasa_aleks.shape[1], column='Fuente', value=['fotocasa' for i in range(fotocasa_aleks.shape[0])])
# fotocasa_aleks.insert(loc=fotocasa_aleks.shape[1], column='Fuente', value=['fotocasa' for i in range(fotocasa_aleks.shape[0])])
#
# fotocasa_aleks = fotocasa_aleks.rename(columns=column_translator)
# fotocasa_aleks = fotocasa_aleks[idealista.columns]
# print(f'Filtered columns on Fotocasa-Aleks dataset: {fotocasa_aleks.columns}')
# merged = pd.concat([fotocasa_aleks, idealista]).reset_index(drop=True)
# merged = merged.drop_duplicates(subset=['Link'], keep='first')
#
# merged.to_csv(path_or_buf='../data/output_concat.csv')

if __name__ == '__main__':

    # Initalization of variables and information fetching

    area_to_scrape = "Vilanova i la Geltrú"
    area_csv_name = unidecode(area_to_scrape).lower().replace(" ", "-")
    execution_timestamp = datetime.today().strftime('%Y-%m-%d')
    fdf = fts.scrape_fotocasa(
        area="Vilanova i la Geltrú",
        csv_name=f"../data/fotocasa_{area_csv_name}_{execution_timestamp}.csv",
        page_index_limit=2
    )
    idf = ids.scrape_idealista(
        csv_name=f"../data/idealista_{area_csv_name}_{execution_timestamp}.csv",
        page_index_limit=2
    )

    # Normalize the names on both DataFrames and add a source column

    fdf = fdf.rename(columns=column_translator)
    idf = idf.rename(columns=column_translator)
    fdf.insert(loc=fdf.shape[1], column='Source', value=['fotocasa' for i in range(fdf.shape[0])])
    idf.insert(loc=idf.shape[1], column='Source', value=['idealista' for i in range(idf.shape[0])])

    # Less columns available on Idealista, so we filter to ensure we have the
    # same information

    fdf_filtered = fdf[idf.columns]

    # Concatenate both datasets and drop possible duplicates, store as csv

    merged = pd.concat([fdf_filtered, idf]).reset_index(drop=True)
    merged = merged.drop_duplicates(subset=['Link'], keep='first')
    merged.to_csv(path_or_buf='../data/output_concat.csv')