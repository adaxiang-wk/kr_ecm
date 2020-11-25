import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
import time
import pandas as pd
# import sys
# import pandas as pd 
# from datetime import datetime, timedelta
# import re
# import csv

class scraper:
    def __init__(self):
        driver_path = r'/Users/adaxiang/chromedriver'
        self.driver = webdriver.Chrome(executable_path=driver_path)
        self.base_url = 'http://dart.fss.or.kr/'

        self.main_window = None
        self.doc_window = None

        # filing doc data points
        self.annouce_dates = []
        self.new_shares = []
        self.second_shares = []
        self.share_outstandings = []
        self.tranche_share_initials = []
        self.tranche_filing_high = []
        self.tranche_filing_low = []

        # offer doc data points
        self.pricing_dates = []


    def search(self, company_name, start_date, end_date):
        print('searching...')
        self.driver.get(self.base_url)
        self.main_window = self.driver.current_window_handle
        
        cpny_name_input = self.driver.find_element_by_id("textCrpNm")
        cpny_name_input.clear()
        cpny_name_input.send_keys(company_name)

        start_date_input = self.driver.find_element_by_id("startDate")
        start_date_input.clear()
        start_date_input.send_keys(start_date)

        end_date_input = self.driver.find_element_by_id("endDate")
        end_date_input.clear()
        end_date_input.send_keys(end_date)

        self.driver.find_element_by_class_name("option_03").click()
        time.sleep(1)
        self.driver.find_element_by_xpath("//input[@title='증권신고(지분증권)']").click()
        self.driver.find_element_by_xpath("//input[@title='증권신고(채무증권)']").click()

        self.driver.find_element_by_xpath("//input[@class='ibtn']").click()
        time.sleep(2)

        # asked to choose a company
        try:
            chosen_cpy = self.driver.find_elements_by_id('checkCorpSelect')
            if len(chosen_cpy) > 0:
                chosen_cpy[0].click()
                enter_btn = self.driver.find_element_by_xpath("//a[@onclick='selectSearchCorp();return false;']")
                enter_btn.click()
                time.sleep(2)
                self.driver.find_element_by_xpath("//select[@name='maxResultsCb']/option[text()='100']").click()
                time.sleep(1)
                self.driver.find_elements_by_id('searchpng')[0].click()
                time.sleep(2)
            else:
                pass
        except selenium.common.exceptions.NoSuchElementException:
            pass

        self.doc_window = self.driver.current_window_handle 

    
    def find_doc(self, doc_name):
        """
        Params: 
            - doc name: string, 'filing_doc' or 'offer_doc'
            - company name: string, issuer company name in Korean
            - start_date: string, search start date, in format yyyymmdd
            - end_date: string, search end date, in format yyyymmdd

        Return:
            - found_doc: boolean, indicating whether the expected doc is found
            - date: string, the desired date in format yyyymmdd
                - for filling doc: filling date/annoucement date
                - for offer doc: TODO
        """
        
        found_doc = False

        if doc_name == 'filing_doc':
            link_text = "증권신고서"
        elif doc_name == 'offer_doc':
            link_text = "투자설명서"

        # self._search(company_name, start_date, end_date)
        docs = self.driver.find_elements_by_partial_link_text(link_text)

        
        if len(docs) <= 0:
            print(f"no {doc_name} found")
            found_doc = False
            return found_doc
        else:
            chosen_doc = docs[-1]
            chosen_doc.click()
            time.sleep(2)

            doc_page = self.driver.window_handles[1]
            self.driver.switch_to.window(doc_page)
            time.sleep(1)

            select_pane = self.driver.find_element_by_xpath(("//select[@id='family']"))
            doc_options = select_pane.find_elements_by_tag_name("option")

            if len(doc_options) > 0:
                 # choose the ealest doc for filing doc 
                 # choose the latest doc for offer doc 
                desired_option = None
                for cur_doc in doc_options:
                    if cur_doc.get_attribute("value") == "null":
                        continue

                    cur_date = int(cur_doc.get_attribute("value")[6:])
                    if desired_option is None:
                        desired_option = cur_doc
                    else:
                        if doc_name == 'offer_doc':
                            if cur_date >= extreme_date:
                                desired_option = cur_doc
                        else:
                            if cur_date < extreme_date:
                                desired_option = cur_doc
                    extreme_date = int(desired_option.get_attribute("value")[6:])
                desired_option.click()

                # waiting for loading 
                side_panel = self.driver.find_elements_by_id('west-panel')
                while len(side_panel) == 0:
                    self.driver.refresh()
                    side_panel = self.driver.find_elements_by_id('west-panel')

                # get doc inside iframe
                iframes = self.driver.find_elements_by_tag_name('iframe')

                if len(iframes) > 0:
                    iframe = iframes[0]
                    self.driver.switch_to_frame(iframe)

                    found_doc = True
                    
                    result_date = str(extreme_date)[:8]
                    if doc_name == "offer_doc":
                        self.pricing_dates.append(result_date)
                    else:
                        self.annouce_dates.append(result_date)
                    return found_doc
                else:
                    print("Doc page not found")
                    found_doc = False
                    return found_doc
                
            else:
                print("no doc options found")
                found_doc = False
                return found_doc


    def get_filing_doc_info(self):
        self.driver.switch_to.default_content()
        self.driver.find_element_by_link_text("2. 공모방법").click()

        iframe = self.driver.find_element_by_tag_name('iframe')
        self.driver.switch_to_frame(iframe)

        target_sentence = self.driver.find_elements_by_xpath("//p[@class='section-2']/following-sibling::p")[1]
        target_words = str(target_sentence.text).split(" ")

        # find new share value
        if "신주모집" in target_words:
            idx = target_words.index("신주모집")
            new_share = int(target_words[idx+1][:-2].replace(",", ""))
            self.new_shares.append(new_share)
        else:
            self.new_shares.append(-1)

        # find second share value
        if "구주매출" in target_words:
            idx = target_words.index("구주매출")
            second_share = int(target_words[idx+1][:-2].replace(",", ""))
            self.second_shares.append(second_share)
        else:
            self.second_shares.append(-1)

        self.driver.switch_to.default_content()

        # find share outstandings 
        self.driver.find_element_by_link_text("4. 주식의 총수 등").click()
        self.driver.switch_to_frame(iframe)

        share_os_name = self.driver.find_element_by_xpath("//*[contains(text(), '유통주식수')]")
        share_os_td = share_os_name.find_element_by_xpath('..')
        share_os_value_td = share_os_td.find_element_by_xpath("./following-sibling::td")
        share_os_value = int(share_os_value_td.find_element_by_tag_name("p").text.replace(",", ""))
        self.share_outstandings.append(share_os_value)
        
        



    def get_offer_doc_info(self):
        
        return 0

    
    # def scrap_batch(self, cp_list, start_date, end_date):
    #     print(f"total {len(cp_list)} companies to scrap")
    #     for idx, cp in enumerate(cp_list):
    #         print(f"scraping {cp}")
    #         self.search(cp, start_date, end_date)
    #         filing_doc_found = self.find_doc("filling_doc")
    #         if filing_doc_found:
    #             filing_doc_found = self.get_filing_doc_info()
    #             self.driver.switch_to.window(self.doc_window)

    #             offer_doc_found = self.find_doc("offer_doc")
    #             if offer_doc_found:
    #                 offer_doc_info = self.get_offer_doc_info()

    #         self.driver.switch_to.window(self.main_window)
    #         print(f"finished {cp}, {len(cp_list)-idx-1} left")

    #     return filing_doc_found, offer_doc_info


                
                




