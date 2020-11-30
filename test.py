from scrapers.KRXscraper import scraper as krx_scraper
from scrapers.DARTscraper import scraper as dart_scraper

import argparse

def test_krxscraper():
    krxscraper = krx_scraper()
    result_df = krxscraper.get_data(startdate='20190601', enddate='20200101')
    print(result_df)


def test_get_filing_doc():
    dartsraper = dart_scraper()
    dartsraper.search(company_name="빅히트엔터테인먼트", start_date="20200524", end_date="20201124")
    is_found = dartsraper.find_doc(doc_name='filing_doc')

    dartsraper.get_filing_doc_info()
    print(f'''Found the doc {is_found}\n
              annoucement_date: {dartsraper.annouce_dates}\n
              new_shares: {dartsraper.new_shares}\n
              second_shares: {dartsraper.second_shares}\n
              share outstandings: {dartsraper.share_outstandings}\n
              tranche filing high range {dartsraper.tranche_filing_high}\n
              tranche filing low range {dartsraper.tranche_filing_low}''')

    dartsraper.driver.quit()


def test_get_offer_doc():
    dartsraper = dart_scraper()
    dartsraper.search(company_name="빅히트엔터테인먼트", start_date="20200524", end_date="20201124")
    is_found = dartsraper.find_doc(doc_name='offer_doc')
    dartsraper.get_offer_doc_info()
    print(f'''Found the doc {is_found}\n
              pricing date: {dartsraper.pricing_dates}\n
              subsprition start date: {dartsraper.sub_startdates}\n
              subsprition end date: {dartsraper.sub_enddates}\n
              settlement date: {dartsraper.settle_dates}\n
              use of proceeds: {dartsraper.uops}\n''')

    dartsraper.driver.quit()


if __name__ == "__main__":
    test_map = {
        'krxscraper':test_krxscraper, 
        'get_filing_doc':test_get_filing_doc, 
        'get_offer_doc':test_get_offer_doc
    }
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-test', type=str, required=True, help=f'choose an action from {test_map.keys()}')

    args = arg_parser.parse_args()
    if args.test == 'all':
        test_krxscraper()
        test_get_filing_doc()
        test_get_offer_doc()
    elif args.test in test_map.keys():
        test_map[args.test]()
    else:
        raise ValueError("No such test available")
    

    

    
    
    