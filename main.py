from src.scrapers.KRXscraper import scraper as krx_scraper
from src.scrapers.DARTscraper import scraper as dart_scraper
import src.data_utils as du

import pandas as pd
import os

DATA_DIR = './data'

DEAL_FILENAME = 'deals_df.csv'
DATA_FILENAME = 'data_df.csv'

SEARCH_START_DATE = '20190601'
SEARCH_END_DATE = '20190901'

COL_NAMES = [
    'ticker',
    'company',
    'first_trade_date',
    'annouce_date',
    'new_shares',
    'second_shares',
    'share_outstandings',
    'tranche_filing_high_range',
    'tranche_filing_low_range',
    'pricing_date',
    'subsprition_start_date',
    'subsprition_end_date',
    'settlement_date',
    'use_of_proceeds',
    'banks',
    'bank_roles',
    'bank_quantity',
    'bank_price',
    'bank_fee',
    'tranche_exchange'
]

if __name__ == "__main__":
    deals_fp = os.path.join(DATA_DIR, DEAL_FILENAME)
    data_fp = os.path.join(DATA_DIR, DATA_FILENAME)

    if os.path.exists(deals_fp):
        deals_df = pd.read_csv(deals_fp)
    else:
        krxscraper = krx_scraper(headless=False)
        deals_df = krxscraper.get_data(startdate=SEARCH_START_DATE,
                                    enddate=SEARCH_END_DATE)

    deals_df = deals_df.iloc[:, :].reset_index()
    
    scrapped_tickers = []
    if os.path.exists(data_fp):
        already_scrapped = pd.read_csv(data_fp)
        scrapped_tickers = list(already_scrapped['ticker'])

    for idx, record in deals_df.iterrows():
        company_name = record['company']
        first_trade_date = record['first_trade_date']
        ticker = record['ticker']

        if len(scrapped_tickers) > 0:
            if ticker in scrapped_tickers:
                print(f"{ticker} already scrapped")
                continue

        print(f"Scrapping {ticker} {company_name}")

        dart_startd_str, dart_endd_str = du.format_search_date_str(str(first_trade_date), days_diff=15)

        dartsraper = dart_scraper()
        data_dict = dartsraper.get_all_info(company_name=ticker,
                            start_date=dart_startd_str,
                            end_date=dart_endd_str)
        
        all_data_list = [ticker, company_name, first_trade_date]
        all_data_list.extend(list(data_dict.values()))

        if idx == 0:
            du.write_to_csv(data_fp, all_data_list, header=COL_NAMES)
        else:
            du.write_to_csv(data_fp, all_data_list)
    