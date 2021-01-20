from selenium import webdriver
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import re
from datetime import datetime

class scraper:
    def __init__(self, headless=False):
        driver_path = r'/Users/adaxiang/chromedriver'
        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless")

        self.driver = webdriver.Chrome(executable_path=driver_path,
                                       options=options)
        self.driver.maximize_window()
        self.base_url = "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201"

    def _sort_result(self):
        self.driver.get(self.base_url)

        while True:
            try:
                header_sec = self.driver.find_element_by_class_name("CI-GRID-HEADER-TABLE-THEAD")
            except NoSuchElementException:
                print('Loading page ...')
                time.sleep(3)
            else:
                break
        self.driver.find_element_by_class_name("btn_content_size_btn").click()
        list_date_sec = header_sec.find_element_by_xpath("//td[@data-name='LIST_DD']")
        # print(list_date_sec.get_attribute("outerHTML"))
        list_date_sec.find_element_by_tag_name("a").click()

        # table_area = self.driver.find_element_by_class_name("CI-GRID-WRAPPER")
        # self.driver.execute_script("arguments[0].scrollBy(arguments[1],arguments[2])", table_area, 0, 5000)
        # time.sleep(2)
        # self.driver.execute_script("arguments[0].scrollBy(arguments[1],arguments[2])", table_area, 5000, 10000)
        # time.sleep(2)
        # print(f"scrolled {height}")
        # time.sleep(3)
        # height += height
        # table_area = self.driver.find_element_by_class_name("CI-GRID-WRAPPER")
        # self.driver.execute_script("arguments[0].scrollBy(0,arguments[1])", table_area, height)

    def _get_tr_data(self, tr):
        tds = tr.find_elements_by_tag_name("td")

        td_data = [td.text for td in tds]
        td_data[5] = datetime.strptime(td_data[5], "%Y/%m/%d").date()
        td_data[-1] = int(td_data[-1].replace(",", ""))
        td_data[-2] = int(td_data[-2].replace(",", ""))

        return td_data



    def _get_data_in_period(self, sdate, edate):
        cols = ['isin',\
                'ticker',\
                'company_name_kr',\
                'event_name_kr',\
                'company_name_en',\
                'price_date',\
                'exchange',
                'security_type',\
                'affiliation',\
                'stock_type',\
                'face_value',\
                'num_listed_shares']
        table_body_sec = self.driver.find_element_by_class_name("CI-GRID-BODY-TABLE-TBODY")
        trs = table_body_sec.find_elements_by_tag_name("tr")

        sdate_obj = datetime.strptime(sdate, "%Y%m%d").date()
        edate_obj = datetime.strptime(edate, "%Y%m%d").date()

        data = []

        for tr in trs:
            tr_data = self._get_tr_data(tr)
            tr_date = tr_data[5]
            if tr_date > edate_obj:
                continue

            if tr_date < sdate_obj:
                break 

            data.append(tr_data)
        
        df = pd.DataFrame(data, columns=cols)
        return df



    def _search_by_date(self, startdate, enddate):
        print(startdate, enddate)
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

        result_table_html = self.driver.find_element_by_class_name(
            "CI-GRID-BODY-TABLE").get_attribute("outerHTML")
        result_df = pd.read_html(result_table_html)[0]
        self.driver.quit()
        return result_df

    # def get_data(self, startdate, enddate):
    #     result_df = self._search_by_date(startdate, enddate)
    #     result_df = result_df.rename(columns={
    #         '종목코드': 'ticker',
    #         '기업명': 'company',
    #         '신규상장일': 'first_trade_date'
    #     })
    #     result_df = result_df.loc[:, ['ticker', 'company', 'first_trade_date']]
    #     result_df['company'] = result_df['company'].apply(
    #         lambda x: re.sub(r'[\(\[].*?[\)\]]', "", x))
    #     result_df['first_trade_date'] = result_df['first_trade_date'].apply(
    #         lambda x: x.replace("/", ""))

    #     return result_df
    def get_data(self, startdate, enddate):
        self._sort_result()
        data = None
        # time.sleep(1)
        # data = self. _get_data_in_period(sdate=startdate, edate=enddate)

        return data
