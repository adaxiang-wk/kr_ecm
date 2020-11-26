from scrapers.KRXscraper import scraper as krx_scraper
from scrapers.DARTscraper import scraper as dart_scraper

if __name__ == "__main__":
    # krxscraper = krx_scraper()
    # result_df = krxscraper._search_by_date(startdate='20190101', enddate='20200101')
    # print(result_df)

    dartsraper = dart_scraper()
    dartsraper.search(company_name="빅히트엔터테인먼트", start_date="20200524", end_date="20201124")
    is_found = dartsraper.find_doc(doc_name='offer_doc')
    dartsraper.get_offer_doc_info()
    print(f'''Found the doc {is_found}\n
              pricing date: {dartsraper.pricing_dates}\n
              subsprition start date: {dartsraper.sub_startdates}\n
              subsprition end date: {dartsraper.sub_enddates}\n
              settlement date: {dartsraper.settle_dates}\n
              use of proceeds: {dartsraper.uops}
              ''')

    
    # dartsraper.get_filing_doc_info()
    # print(f'''Found the doc {is_found}\n
    #           annoucement_date: {dartsraper.annouce_dates}\n
    #           new_shares: {dartsraper.new_shares}\n
    #           second_shares: {dartsraper.second_shares}\n
    #           share outstandings {dartsraper.share_outstandings}\n''')
    dartsraper.driver.quit()