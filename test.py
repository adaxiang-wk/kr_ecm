from scrapers.KRXscraper import scraper as krx_scraper

if __name__ == "__main__":
    krxscraper = krx_scraper()
    result_df = krxscraper._search_by_date(startdate='20190101', enddate='20200101')
    print(result_df)