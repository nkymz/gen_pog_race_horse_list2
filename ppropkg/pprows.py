# -*- coding: utf-8 -*-

import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
# import pprint

NEXT_RACE_INFO_URL = "http://pog-info.com/archives/category/pog/news"
NEXT_RACE_ARTICLE_URL = "http://pog-info.com/archives/{}"
WEBDRIVERPATH = r"C:\Selenium\chromedriver.exe"
JRA_DF_URL = "http://www.jra.go.jp/datafile/"
NK_AUTH_URL = "https://regist.netkeiba.com/account/?pid=login"
NK_BM_URL = "https://race.netkeiba.com/?pid=bookmark&rf=navi"
NK_BM_RACE_XP = """
//div[contains(@class , 'BMHorseDataArea')][{}]//table[contains(@class, 'BMHorseDataTable')][{}]//a
"""
NK_BM_HORSE_XP = """
//div[contains(@class , 'BMHorseDataArea')][{}]//table[contains(@class, 'BMHorseDataTable')][{}]//tbody/tr[{}]//a
"""
NK_BM_DATE_XP = """
//div[contains(@class , 'BMHorseDataArea')][{}]//h2
"""
NK_BM_CS_RN_XP = """
//div[contains(@class , 'BMHorseDataArea')][{}]//table[contains(@class, 'BMHorseDataTable')][{}]//th[1]
"""
NK_BM_GRADE_XP = """
//div[contains(@class , 'BMHorseDataArea')][{}]//table[contains(@class, 'BMHorseDataTable')][{}]//a/../span
"""
NK_BM_STATE_XP = """
//div[contains(@class , 'BMHorseDataArea')][{}]//table[contains(@class, 'BMHorseDataTable')][{}]//th[3]
"""

NK_BM_NEXT_WEEK_XP = """
//div[contains(@class , 'RaceDayNext')]/a
"""


class NetKeiba:

    def __init__(self, nk_id, nk_pw, seconds, *args):
        options = Options()
        if "headless" in args:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path=WEBDRIVERPATH, options=options)
        self.driver.get(NK_AUTH_URL)
        self.seconds = seconds
        time.sleep(seconds)
        self.driver.find_element_by_xpath("//input[contains(@name, 'login_id')]").send_keys(nk_id)
        self.driver.find_element_by_xpath("//input[contains(@name, 'pswd')]").send_keys(nk_pw)
        self.driver.find_element_by_xpath("//input[contains(@alt, 'ログイン')]").click()

    def get_race_horse_list(self, is_sp_reg):
        time.sleep(self.seconds)
        race_horse_list_short = []
        self.driver.get(NK_BM_URL)
        h = 1

        while True:
            i, j, k = 1, 1, 1
            if h > 1:
                if is_sp_reg:
                    try:
                        self.driver.find_element_by_xpath(NK_BM_NEXT_WEEK_XP).click()
                    except NoSuchElementException:
                        break
                else:
                    break

            while True:
                j, k = 1, 1
                try:
                    race_mmdd_jpn = self.driver.find_element_by_xpath(NK_BM_DATE_XP.format(i)).text
                except NoSuchElementException:
                    break
                race_month = int(race_mmdd_jpn.split("月")[0])
                race_day = int(race_mmdd_jpn.split("月")[1].split("日")[0])
                race_weekday = race_mmdd_jpn.split("（")[1].split("）")[0]
                while True:
                    k = 1
                    try:
                        race_url = self.driver.find_element_by_xpath(NK_BM_RACE_XP.format(i, j)).get_attribute("href")
                    except NoSuchElementException:
                        break
                    race_status = self.driver.find_element_by_xpath(NK_BM_STATE_XP.format(i, j)).text
                    if is_sp_reg and race_status != "特別登録" or not is_sp_reg and race_status == "特別登録":
                        j += 1
                        continue
                    try:
                        race_grade = self.driver.find_element_by_xpath(NK_BM_GRADE_XP.format(i, j)).text
                    except NoSuchElementException:
                        race_grade = None
                    track_and_race_no = self.driver.find_element_by_xpath(NK_BM_CS_RN_XP.format(i, j)).text
                    track = track_and_race_no[0:2]
                    race_no = ("0" + track_and_race_no[2:])[-3:]
                    race_id = race_url.split("=")[-1][1:]
                    race_year = int(race_id[0:4])
                    while True:
                        try:
                            horse_url = self.driver.find_element_by_xpath(NK_BM_HORSE_XP.format(i, j, k))\
                                .get_attribute("href")
                        except NoSuchElementException:
                            break
                        horse_id = horse_url[-11:-1]
                        horse_name = self.driver.find_element_by_xpath(NK_BM_HORSE_XP.format(i, j, k)).text
                        race_horse_list_short.append([race_year, race_month, race_day, race_weekday, track, race_id,
                                                      race_grade, race_no, race_status, horse_id,
                                                      horse_url, horse_name])
                        k += 1
                    j += 1
                i += 1
            h += 1

        return race_horse_list_short

    def quit(self):
        self.driver.quit()


class JRAHorseSearch:

    def __init__(self, *args):
        options = Options()
        if "headless" in args:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path=WEBDRIVERPATH, options=options)
        time.sleep(1)
        self.driver.get(JRA_DF_URL)
        time.sleep(1)
        self.driver.find_element_by_xpath("//img[@alt='競走馬検索']/../..").click()

    def get_status(self, horse_name):
        time.sleep(1)
        self.driver.find_element_by_xpath("//td[contains(text(), '競走馬名')]/following-sibling::td[1]/input").clear()
        self.driver.find_element_by_xpath("//td[contains(text(), '競走馬名')]/following-sibling::td[1]/input")\
            .send_keys(horse_name)
        self.driver.find_element_by_id("iv_hmaskbn1").click()
        self.driver.find_element_by_xpath("//td[contains(text(), '競走馬名')]/following-sibling::td[1]/a").click()
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath("//a[contains(text(), '" + horse_name + "')]").click()
        except NoSuchElementException:
            return "未登録"
        if self.driver.find_elements_by_xpath("//td[contains(text(), '放牧')]"):
            self.driver.find_element_by_xpath("//a[@href='javascript:history.back()']").click()
            return "放牧"
        else:
            self.driver.find_element_by_xpath("//a[@href='javascript:history.back()']").click()
            return "非放牧"

    def quit(self):
        self.driver.quit()


class SoupNK:

    def __init__(self, parser, seconds, login_id, password):
        self.parser = parser
        self.seconds = seconds
        LOGIN_INFO = {
            'pid': 'login',
            'action': 'auth',
            'return_url2': '',
            'mem_tp': '',
            'login_id': login_id,
            'pswd': password,
            'auto_login': ''
        }
        self.mysession = requests.Session()
        login_url = "https://regist.netkeiba.com/account/"
        time.sleep(seconds)
        self.mysession.post(login_url, data=LOGIN_INFO)

    def get(self, target_url, *args):
        time.sleep(self.seconds)
        r = self.mysession.get(target_url)
        if r.status_code == requests.codes.ok:
            if "ignore_euc-jp" in args:
                return BeautifulSoup(r.content.decode("euc-jp", "ignore").encode("euc-jp"), self.parser)
            else:
                return BeautifulSoup(r.content, self.parser)
        else:
            return None


class Soup:

    def __init__(self, target_url, parser, seconds):
        self.target_url = target_url
        self.parser = parser
        self.seconds = seconds

    def get(self):
        time.sleep(self.seconds)
        r = requests.get(self.target_url)
        if r.status_code == requests.codes.ok:
            return BeautifulSoup(r.content, self.parser)
        else:
            return None


def get_next_race_info_id():
    soup = Soup(NEXT_RACE_INFO_URL, "lxml", 1)
    html = soup.get()
    return html.find("article").get("id").split("-")[1]


def get_next_race_info(article_id):
    soup = Soup(NEXT_RACE_ARTICLE_URL.format(article_id), "lxml", 1)
    next_race_content = soup.get().find("div", class_="single-entry-content")
    return next_race_content


def main():
    pass


if __name__ == "__main__":
    main()
