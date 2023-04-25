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
    'info_card_type': 'Type',
    'parking': 'Parking',
    'surface': 'M2'
}

if __name__ == '__main__':

    # Initalization of variables and information fetching

    area_to_scrape = "Vilanova i la Geltrú"
    fdf = fts.scrape_fotocasa(area=area_to_scrape, page_index_limit=2)

    # as the URL construction is considerably harder for Idealista, it is
    # hardcoded to scrape the area "Vilanova i la Geltrú"

    idf = ids.scrape_idealista(page_index_limit=2)

    ## Normalize the names on both DataFrames and add a source column

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
    merged.to_csv(path_or_buf='../data/output_concat.csv', index=False)