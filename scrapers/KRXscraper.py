from selenium import webdriver
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import re

class scraper:
    def __init__(self):
        driver_path = r'/Users/adaxiang/chromedriver'
        self.driver = webdriver.Chrome(executable_path=driver_path)
        self.base_url = "http://marketdata.krx.co.kr/mdi#document=04060401"

    def _search_by_date(self, startdate, enddate):
        self.driver.get(self.base_url)
        while True:
            try:
                self.driver.find_element_by_name("fromdate")
            except NoSuchElementException:
                print('Loading page ...')
                time.sleep(3)
            else:
                break
        fromdate_input = self.driver.find_element_by_name("fromdate")
        fromdate_input.clear()
        fromdate_input.send_keys(startdate)
        todate_input = self.driver.find_element_by_name("todate")
        todate_input.clear()
        todate_input.send_keys(enddate)

        while True:
            try: 
                self.driver.find_element_by_class_name("CI-GRID-ALIGN-CENTER")
            except NoSuchElementException:
                print('Loading search results ...')
                time.sleep(3)
            else:
                print('search results loaded')
                break
        
        result_table_html = self.driver.find_element_by_class_name("CI-GRID-BODY-TABLE").get_attribute("outerHTML")
        result_df = pd.read_html(result_table_html)[0]
        self.driver.quit()
        return result_df


    def get_data(self, startdate, enddate):
        result_df = self._search_by_date(startdate, enddate)
        result_df = result_df.rename(columns={'종목코드':'ticker', '기업명':'company', '신규상장일':'first_trade_date'})
        result_df = result_df.loc[:, ['ticker', 'company', 'first_trade_date']]
        result_df['company'] = result_df['company'].apply(lambda x: re.sub(r'[\(\[].*?[\)\]]', "", x))
        result_df['first_trade_date'] = result_df['first_trade_date'].apply(lambda x: x.replace("/", ""))

        return result_df



    
        




