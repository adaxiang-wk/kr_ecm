import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
import time
import pandas as pd
import re
from selenium.common.exceptions import NoSuchElementException
# from bs4 import BeautifulSoup
# import sys
# import pandas as pd
# from datetime import datetime, timedelta
# import re
# import csv

UOP_DICT = {
    "운영자금": "General Corporate Purposes",
    "시설자금": "Capital Expenditures",
    "차환": "Repay Debt",
    "상환": "Repay Debt",
    "타법인주식획득": "Acquisitions",
    "연구개발비": "Research and development",
    "연구개발": "Research and development",
}


class scraper:
    def __init__(self, headless=False):
        driver_path = r'/Users/adaxiang/chromedriver'
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path=driver_path,
                                       options=options)
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
        self.sub_startdates = []
        self.sub_enddates = []
        self.settle_dates = []
        self.uops = []
        self.tranche_bank_roles = []
        self.tranche_bank_names = []
        self.tranche_bank_quant = []
        self.tranche_bank_price = []
        self.tranche_bank_fee = []
        self.tranche_exchange = []
        self.tranche_general = []
        self.tranche_investor = []
        self.tranche_employee = []
        self.total_share = []

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
        self.driver.find_element_by_xpath(
            "//input[@title='증권신고(지분증권)']").click()
        self.driver.find_element_by_xpath(
            "//input[@title='증권신고(채무증권)']").click()

        self.driver.find_element_by_xpath("//input[@class='ibtn']").click()
        time.sleep(2)

        # asked to choose a company
        try:
            chosen_cpy = self.driver.find_elements_by_id('checkCorpSelect')
            if len(chosen_cpy) > 0:
                chosen_cpy[0].click()
                enter_btn = self.driver.find_element_by_xpath(
                    "//a[@onclick='selectSearchCorp();return false;']")
                enter_btn.click()
                time.sleep(2)
                self.driver.find_element_by_xpath(
                    "//select[@name='maxResultsCb']/option[text()='100']"
                ).click()
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

            select_pane = self.driver.find_element_by_xpath(
                ("//select[@id='family']"))
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
                    extreme_date = int(
                        desired_option.get_attribute("value")[6:])
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


        target_sentences = self.driver.find_elements_by_xpath("//*[contains(text(), '신주모집')]")
        if len(target_sentences) > 0:
            target_sentence = target_sentences[0].text
            target_words = str(target_sentence).split(" ")

            # find new share value
            if "신주모집" in target_words:
                idx = target_words.index("신주모집")
                value_str = target_words[idx + 1].replace(",", "")
                val_lists = re.findall(r"\d{4,}", value_str) 
                if len(val_lists) > 0:
                    value = val_lists[0]
                    new_share = int(value)
                    self.new_shares.append(new_share)
                else:
                    self.new_shares.append(-1)
        
            # find second share value
            if "구주매출" in target_words:
                idx = target_words.index("구주매출")
                second_value_str = target_words[idx + 1].replace(",", "")
                second_val_lists = re.findall(r"\d{4,}", second_value_str)
                if len(second_val_lists) > 0:
                    second_value = second_val_lists[0]
                    second_share = int(second_value)
                else:
                    second_share = -1
                self.second_shares.append(second_share)
            else:
                self.second_shares.append(-1)
        else:
            self.new_shares.append(-1)
            self.second_shares.append(-1)

        tranche_tables_c = self.driver.find_elements_by_tag_name("table")
        found_tranche_table = False
        table_html = ""
        for t in tranche_tables_c:
            table_html = t.get_attribute("outerHTML")
            if ("기관투자자" in table_html) and (any(["100.0%" in table_html, "100%" in table_html, "100.00%" in table_html])):
                found_tranche_table = True
                break 

        if found_tranche_table:
            tranche_df = pd.read_html(table_html)[0]
            tranche_df = tranche_df.reset_index(drop=True)

            korean_dict = {
                "우리사주조합": "employee_tranche", 
                "기관투자자": "investor_tranche", 
                "일반청약자": "general_tranche", 
                "일반투자자": "general_tranche",
                "합계": "total_share"
            }


            for _, row in tranche_df.iterrows():
                row = row.tolist()
                if row[0] in korean_dict.keys():
                    tranche_name = korean_dict[row[0]]

                    if tranche_name == "employee_tranche":
                        self.tranche_employee.append(row[1])
                    elif tranche_name == "investor_tranche":
                        self.tranche_investor.append(row[1])
                    elif tranche_name == "total_share":
                        self.total_share.append(row[1])
                    elif tranche_name == "general_tranche":
                        self.tranche_general.append(row[1])
                else:
                    continue

        # tranche_tables_ls = []
        # for t in tranche_tables:
        #     if len(t.text) > 5:
        #         continue
        #     # print(t.get_attribute("outerHTML"))
        #     tables = t.find_elements_by_xpath("//ancestor-or-self::table")
        #     for table in tables:
        #         table_html = table.get_attribute("outerHTML")

        #         if ("100.0%" not in table_html) and ("100%" not in table_html) and ("100.00%" not in table_html):
        #             continue
        #         else:
        #             tranche_tables_ls.append(table_html)

        # tranche_table_html = tranche_tables_ls[0]
        # print(tranche_table_html)

        self.driver.switch_to.default_content()

        # find share outstandings
        self.driver.find_element_by_link_text("4. 주식의 총수 등").click()
        self.driver.switch_to_frame(iframe)

        share_os_name = self.driver.find_element_by_xpath(
            "//*[contains(text(), '유통주식수')]")
        share_os_td = share_os_name.find_element_by_xpath('..')

        if len(share_os_td.find_elements_by_tag_name("td")) == 0:
            share_os_td = share_os_name.find_element_by_xpath('../..')

        share_os_value_td = share_os_td.find_elements_by_tag_name("td")[1]

        try:
            share_os_value_sec = share_os_value_td.find_element_by_tag_name("p")
        except NoSuchElementException:
            share_os_value_sec = share_os_value_td

        share_os_value_str = share_os_value_sec.text.replace(",", "")
        if share_os_value_str.isdigit():
            share_os_value = int(share_os_value_str)
        else:
            share_os_value = -1

        self.share_outstandings.append(share_os_value)

        # find tranche filing range
        self.driver.switch_to.default_content()
        self.driver.find_element_by_link_text("제1부 모집 또는 매출에 관한 사항").click()
        self.driver.switch_to_frame(iframe)

        target_section = self.driver.find_element_by_xpath(
            "//*[contains(text(), '주2)')]")
        target_text = target_section.find_element_by_xpath(
            "./following-sibling::td").text
        target_text = re.sub(r"\s+|,", "", target_text)
        range_re = r"[0-9]+원~[0-9]+원"
        search_result = re.search(range_re, target_text, re.IGNORECASE)
        if search_result is not None:
            range_text = search_result.group().split("~")
            high_range = int(range_text[-1][:-1])
            low_range = int(range_text[0][:-1])
        else:
            high_range = -1
            low_range = -1

        self.tranche_filing_high.append(high_range)
        self.tranche_filing_low.append(low_range)

    def get_offer_doc_info(self):
        self.driver.switch_to.default_content()
        self.driver.find_element_by_link_text("제1부 모집 또는 매출에 관한 사항").click()

        iframe = self.driver.find_element_by_tag_name('iframe')
        self.driver.switch_to_frame(iframe)

        tables_obj = self.driver.find_elements_by_xpath(
            "//p[@class='section-2']/following-sibling::table")[1:4]

        tables_dfs = {}
        reach_last = False
        for table_obj in tables_obj:
            if reach_last:
                break
            table_html = table_obj.get_attribute("outerHTML")
            # print(">>>>>>>>>>>>>>>>>>>>>")
            # print(table_html)
            df = pd.read_html(table_html)[0]
            if "청약기일" in str(table_html):
                reach_last = True 
                tables_dfs.update({'date_df': df})
            elif "인수인" in str(table_html):
                tables_dfs.update({'bank_df': df})
            else:
                tables_dfs.update({'other_df': df})

        dates_table = tables_dfs['date_df']
        # subscription date
        if '청약기일' not in dates_table.columns:
            col_names = dates_table.iloc[0]
            dates_table = dates_table[1:]
            dates_table.columns = col_names
            dates_table = dates_table.reset_index(drop=True)

        dates_str = dates_table.loc[0, '청약기일'].replace('.', "")
        if "년" in dates_str:
            digits = re.findall(r"\d+|~", dates_str)  
            digits_str = "".join(digits)
            subdates = re.split(r"~", digits_str)
        else:
            subdates = re.split(r"\s|~", dates_str)
            subdates = [re.sub(r"[\(\[].*?[\)\]]", "", date) for date in subdates if len(date) > 0]
        print(subdates)
        self.sub_startdates.append(subdates[0])
        self.sub_enddates.append(subdates[-1])

        # settlement date
        settledate_str = dates_table.loc[0, '납입기일'].replace(".", "")
        if "년" in settledate_str:
            digits = re.findall(r"\d+", settledate_str)  
            settledate = "".join(digits)
        else:
            settledate = settledate_str
        if len(settledate) > 8:
            settledate = re.sub(r"[\(\[].*?[\)\]]", "", settledate)
        self.settle_dates.append(settledate)

        # bookrunner info
        bank_df = tables_dfs['bank_df']
        if '인수인' not in bank_df.columns:
            col_names = bank_df.iloc[0]
            bank_df = bank_df[1:]
            bank_df.columns = col_names
            bank_df = bank_df.reset_index(drop=True)
            if bank_df.columns[0] == bank_df.columns[1]:
                cols = list(bank_df.columns)
                cols[1] = f"{cols[0]}.1"
                bank_df.columns = cols 

        bank_col_dict = {
            "인수인": "bank_role",
            "인수인.1": "bank_name",
            "인수수량": "quantity",
            "인수금액": "gross_price",
            "인수대가": "bank_fee",
        }
        bank_df = bank_df.rename(columns=bank_col_dict)
        bank_df = bank_df.loc[:, list(bank_col_dict.values())]

        bank_role_dict = {
            "공동대표주관회사": "bookrunner",
            "공동주관회사": "bookrunner",
            "대표주관회사": "lead_bookrunner",
            "인수회사": "co_manager"
        }
        bank_df['bank_role'] = bank_df['bank_role'].apply(
            lambda x: bank_role_dict[x]
            if x.strip() in list(bank_role_dict.keys()) else 'bookrunner')
        self.tranche_bank_roles.append(list(bank_df['bank_role']))
        self.tranche_bank_names.append(list(bank_df['bank_name']))
        self.tranche_bank_quant.append(list(bank_df['quantity']))
        self.tranche_bank_price.append(list(bank_df['gross_price']))
        self.tranche_bank_fee.append(list(bank_df['bank_fee']))

        # tranche exchange
        exchange_section = self.driver.find_element_by_xpath(
            "//*[contains(text(), '주7)')]")

        try:
            exchange_text_sec = exchange_section.find_element_by_xpath(
            "./following-sibling::td")
        except:
            exchange_text_sec = exchange_section.find_element_by_xpath(
            "../following-sibling::td")

        exchange_text = exchange_text_sec.text

        if "유가증권시장" in exchange_text:
            self.tranche_exchange.append('KOSPI')
        else:
            self.tranche_exchange.append('KOSDAQ')

        self.driver.switch_to.default_content()

        # use of proceeds
        self.driver.find_element_by_partial_link_text("자금의 사용목적").click()
        self.driver.switch_to_frame(iframe)

        # uop_section = self.driver.find_elements_by_xpath(
        #     "//*[contains(text(), '자금의 사용 계획')]")
        # if len(uop_section) > 0:
        #     uop_section = uop_section[0].find_element_by_xpath('.')

        #     uop_table = uop_section.find_elements_by_xpath(
        #         "./following-sibling::table")[0]
        #     if len(uop_table.find_elements_by_tag_name("tr")) < 2:
        #         uop_table = uop_section.find_elements_by_xpath(
        #         "./following-sibling::table")[1]
        #     uop_table = uop_table.get_attribute("outerHTML")
        #     uop_df = pd.read_html(uop_table)[0]
        #     print(uop_df)
        #     uop_cols = list(uop_df.columns)

        #     for col in uop_cols:
        #         for k in UOP_DICT.keys():
        #             if k in col:
        #                 self.uops.append(UOP_DICT[k])
        #                 break
                    
        # else:
        uop_sections = self.driver.find_elements_by_xpath(
            "//*[contains(text(), '2. 자금의 사용 목적')]")


        if len(uop_sections) < 1:
            uop_sections = self.driver.find_elements_by_xpath(
                "//*[contains(text(), '2. 자금의 사용목적')]")


        if len(uop_sections) > 0:
            
            uop_section = uop_sections[0].find_element_by_xpath('..')
            uop_table = uop_section.find_elements_by_xpath(
                "./following-sibling::table")
            if len(uop_table) < 1:
                uop_section = uop_sections[0].find_element_by_xpath('.')

            if len(uop_table) > 0:
                uop_table = uop_section.find_elements_by_xpath(
                    "./following-sibling::table")
                if len(uop_table) > 0:
                    table = uop_table[0]
                    if len(table.find_elements_by_tag_name("tr")) < 2:
                        table = uop_table[1]
                    uop_table_html = table.get_attribute("outerHTML")
                    uop_df = pd.read_html(uop_table_html)[0]
                    print(uop_df)


                    for col in uop_df.columns:
                        for k in UOP_DICT.keys():
                            if not isinstance(col, int):
                                if k in col:
                                    self.uops.append(UOP_DICT[k])
                                    break
                            
                    
                    if len(self.uops) < 1:
                        for _, row in uop_df.iterrows():
                            row = row.to_list()
                            for k in UOP_DICT.keys():
                                if isinstance(row[0], str):
                                    if k in row[0]:
                                        self.uops.append(UOP_DICT[k])
                                        break
                                elif isinstance(row[1], str):
                                    if k in row[1]:
                                        self.uops.append(UOP_DICT[k])
                                        break
                                    



    def get_all_info(self, company_name, start_date, end_date):
        self.search(company_name, start_date, end_date)

        filing_doc_found = self.find_doc("filing_doc")
        if filing_doc_found:
            self.get_filing_doc_info()
            self.driver.close()
            self.driver.switch_to.window(self.doc_window)

        offer_doc_found = self.find_doc("offer_doc")
        if offer_doc_found:
            self.get_offer_doc_info()
            self.driver.close()
            self.driver.switch_to.window(self.doc_window)

        all_data_points = {
            'annouce_date': self.annouce_dates,
            'new_shares': self.new_shares,
            'second_shares': self.second_shares,
            'share_outstandings': self.share_outstandings,
            'tranche_filing_high_range': self.tranche_filing_high,
            'tranche_filing_low_range': self.tranche_filing_low,
            'pricing_date': self.pricing_dates,
            'subsprition_start_date': self.sub_startdates,
            'subsprition_end_date': self.sub_enddates,
            'settlement_date': self.settle_dates,
            'use_of_proceeds': self.uops,
            'banks': self.tranche_bank_names,
            'bank_roles': self.tranche_bank_roles,
            'bank_quantity': self.tranche_bank_quant,
            'bank_price': self.tranche_bank_price,
            'bank_fee': self.tranche_bank_fee,
            'tranche_exchange': self.tranche_exchange, 
            'tranche_general': self.tranche_general,
            'tranche_investor': self.tranche_investor, 
            'tranche_employee': self.tranche_employee,
            'total_share': self.total_share
        }

        return all_data_points

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
