from src.scrapers.KRXscraper import scraper as krx_scraper
from src.scrapers.DARTscraper import scraper as dart_scraper
import src.data_utils as du

import pandas as pd
import os
import ast
import re

DATA_DIR = './data'

DEAL_FILENAME = 'deals_df_test.csv'
DATA_FILENAME = 'data_df_test.csv'

SEARCH_START_DATE = '20201207'
SEARCH_END_DATE = '20201224'


def clean_data(save_fp=""):
    def clean_int_list(ls):
        ls = ast.literal_eval(ls)
        if len(ls) == 0:
            return ls
        else:
            ls = [int(i) for i in ls]
            return ls

    def get_price_perc(price_str):
        price_str = price_str.replace(",", "")
        price_str = price_str.replace(" ", "")
        price_pattern = r'\d+주'
        perc_pattern = r'\d+.\d+%'

        price = re.findall(price_pattern, price_str)
        if len(price) > 0:
            price = int(price[0][:-1])
        else:
            price = -1

        perc = re.findall(perc_pattern, price_str)
        if len(perc) > 0:
            perc = float(perc[0][:-1])
        else:
            perc = -1.0

        return [price, perc]

    data_fp = os.path.join(DATA_DIR, DATA_FILENAME)
    df = pd.read_csv(data_fp)
    df.loc[:, ['banks']] = df['banks'].apply(lambda x: x
                                             if x == '[]' else x[1:-1])
    df.loc[:, ['bank_roles']] = df['bank_roles'].apply(
        lambda x: x if x == '[]' else x[1:-1])

    df.loc[:, ['bank_quantity']] = df['bank_quantity'].apply(
        lambda x: x if x == '[]' else x[1:-1])
    df.loc[:, ['bank_quantity']] = df['bank_quantity'].apply(
        lambda x: clean_int_list(x))

    df.loc[:, ['bank_price']] = df['bank_price'].apply(
        lambda x: x if x == '[]' else x[1:-1])
    df.loc[:, ['bank_price']] = df['bank_price'].apply(
        lambda x: clean_int_list(x))

    df.loc[:, ['bank_fee']] = df['bank_fee'].apply(lambda x: x
                                                   if x == '[]' else x[1:-1])
    df.loc[:, ['bank_fee']] = df['bank_fee'].apply(lambda x: clean_int_list(x))

    df.loc[:, ['use_of_proceeds']] = df['use_of_proceeds'].apply(
        lambda x: list(set(ast.literal_eval(x))))

    df.loc[:, ['tranche_general']] = df['tranche_general'].apply(
        lambda x: get_price_perc(x))
    df.loc[:, ['tranche_investor']] = df['tranche_investor'].apply(
        lambda x: get_price_perc(x))
    df.loc[:, ['tranche_employee']] = df['tranche_employee'].apply(
        lambda x: get_price_perc(x))
    df.loc[:, ['total_share']] = df['total_share'].apply(
        lambda x: get_price_perc(x))

    if len(save_fp) > 0:
        df.to_csv(save_fp, index=False)
    else:
        df.to_csv(data_fp, index=False)


def scrape_data_to_csv():
    deals_fp = os.path.join(DATA_DIR, DEAL_FILENAME)
    data_fp = os.path.join(DATA_DIR, DATA_FILENAME)

    if os.path.exists(deals_fp):
        deals_df = pd.read_csv(deals_fp)
    else:
        krxscraper = krx_scraper(headless=False)
        deals_df = krxscraper.get_data(startdate=SEARCH_START_DATE,
                                       enddate=SEARCH_END_DATE)
        deals_df.to_csv(deals_fp)

    deals_df = deals_df.iloc[:, :].reset_index()

    scrapped_tickers = []
    if os.path.exists(data_fp):
        already_scrapped = pd.read_csv(data_fp)
        scrapped_tickers = list(already_scrapped['ticker'])

    for idx, record in deals_df.iterrows():
        price_date = record['price_date']
        ticker = record['ticker']

        if len(scrapped_tickers) > 0:
            if ticker in scrapped_tickers:
                print(f"{ticker} already scrapped")
                continue

        print(f"Scrapping {ticker}")

        dart_startd_str, dart_endd_str = du.format_search_date_str(
            str(price_date), days_diff=30)

        dartsraper = dart_scraper()
        data_dict = dartsraper.get_all_info(company_name=ticker,
                                            start_date=dart_startd_str,
                                            end_date=dart_endd_str)

        all_data_list = record.to_list()
        all_data_list.extend(list(data_dict.values()))
        col_name = list(deals_df.columns)
        col_name.extend(list(data_dict.keys()))

        if idx == 0:
            du.write_to_csv(data_fp, all_data_list, header=col_name)
        else:
            du.write_to_csv(data_fp, all_data_list)


if __name__ == "__main__":
    scrape_data_to_csv()
    clean_data(save_fp="./data/cleaned_data_df_test.csv")