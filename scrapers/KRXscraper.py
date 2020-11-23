from selenium import webdriver
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

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



    
        




