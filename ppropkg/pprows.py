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
NK_TRAINING_URL = """
http://race.netkeiba.com/?pid=race&id=c{}&mode=oikiri
"""
NK_LOCAL_TRAINING_URL = """
http://nar.netkeiba.com/?pid=race&id=c{}&mode=oikiri
"""
NK_PREDICTIONS_URL = """
http://race.netkeiba.com/?pid=yoso&id=c{}
"""
NK_LOCAL_PREDICTIONS_URL = """
http://nar.netkeiba.com/?pid=yoso&id=c{}
"""
NK_STABLE_COMMENT_URL = """
https://race.netkeiba.com/race/comment.html?race_id={}
"""
NK_LOCAL_STABLE_COMMENT_URL = """
http://nar.netkeiba.com/?pid=race_old&id=c{}&mode=comment
"""
NK_BM_RACE_XP = """
//*[@id="horse_bookmark"]/section/div[{}]/table[{}]/thead/tr/th[2]/div/p/a
"""
NK_BM_LOCAL_RACE_XP = """
//*[@id="horse_bookmark"]/section/table[{}]/thead/tr/th[2]/div/p/a
"""
NK_BM_HORSE_XP = """
//*[@id="horse_bookmark"]/section/div[{}]/table[{}]/tbody/tr[{}]/td[2]/a
"""
NK_BM_LOCAL_HORSE_XP = """
//*[@id="horse_bookmark"]/section/table[{}]/tbody/tr[{}]/td[2]/a
"""
NK_BM_DATE_XP = """
//*[@id='horse_bookmark']/section/div[{}]/h2
"""
NK_BM_CS_RN_XP = """
//*[@id="horse_bookmark"]/section/div[{}]/table[{}]/thead/tr/th[1]
"""
NK_BM_LOCAL_CS_RN_XP = """
//*[@id="horse_bookmark"]/section/table[{}]/thead/tr/th[1]
"""
NK_BM_GRADE_XP = """
//*[@id="horse_bookmark"]/section/div[{}]/table[{}]/thead/tr/th[2]/div/p/span
"""
NK_BM_LOCAL_GRADE_XP = """
//*[@id="horse_bookmark"]/section/table[{}]/thead/tr/th[2]/div/p/span
"""
NK_BM_STATE_XP = """
//*[@id="horse_bookmark"]/section/div[{}]/table[{}]/thead/tr/th[3]/div
"""
NK_BM_LOCAL_STATE_XP = """
//*[@id="horse_bookmark"]/section/table[{}]/thead/tr/th[3]/div
"""
NK_BM_NEXT_WEEK_XP = """
//*[@id="horse_bookmark"]/section/div[2]/div[2]/a
"""
NK_BM_PREVIOUS_WEEK_XP = """
//*[@id="horse_bookmark"]/section/div[2]/div[1]/a
"""
NK_BM_NEXT_DAY_XP = """
//*[@id="horse_bookmark"]/section/div[2]/div[2]/a
"""
NK_BM_LOCAL_XP = """
//*[@id="horse_bookmark"]/div[2]/ul/li[2]/a
"""
NK_BM_LOCAL_DATE_XP = """
//*[@id="horse_bookmark"]/section/div[2]/p
"""
NK_RACE_NAME_XPold = """
//*[@id="main"]/div/div/div[4]/div/dl/dd/h1
"""
NK_RACE_NAME_XP = """
//*[@class_="RaceName"]
"""
NK_RACE_NAME_XP_SP = """
//dl[contains(concat(' ',normalize-space(@class),' '),' racedata ') and contains(concat(' ',normalize-space(@class),' '),' fc ')]/dd/h1
"""
NK_LOCAL_RACE_NAME_XP = """
//*[@id="main"]/div[3]/div/div[3]/div/dl/dd/h1
"""
NK_RACE_COURSE_XP = """
//*[@id="main"]//dl/dd/p[{}]
"""
NK_RACE_COURSE_XP_SP = """
//*[@id="main"]//dl/dd/p[{}]
"""
NK_LOCAL_RACE_COURSE_XP = """
//*[@id="main"]/div[3]/div/div[3]/div/dl/dd/p[{}]/span
"""
NK_RACE_INFO_XPold = """
//*[@id="main"]/div/div/div[4]/div/div/p[{}]
"""
NK_RACE_INFO_XP = """
//*[@id="main"]//div[@class="race_otherdata"]/p[{}]
"""
NK_RACE_INFO_XP_SP = """
//*[@id="main"]//div[@class="race_otherdata"]/p[{}]
"""
NK_LOCAL_RACE_INFO_XP = """
//*[@id="main"]/div[3]/div/div[3]/div/div/p[{}]
"""

NK_TRAINING_XP = """
//table[@id="All_Oikiri_Table"]/tbody
"""

NK_PREDICTIONS_XP = """
//div[@id="race_main"]/table/tbody
"""

NK_STABLE_COMMENT_XP = """
//table[@id="All_Comment_Table"]/tbody
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

    def get_race_detail(self, race_url, horse_url, race_status, race_id, horse_name, is_local, status):
        self.driver.get(race_url)
        time.sleep(self.seconds)
        if not is_local:
            race_name = self.driver.find_element_by_class_name("RaceName").text
            racedata01 = self.driver.find_element_by_class_name("RaceData01").text
            race_cond2 = self.driver.find_element_by_class_name("RaceData02").text
            race_time = "--:--"
            weather = ""
            course_condition = ""
            if len(racedata01.split("/")) == 1:
                course = racedata01.split("/")[0]
            elif len(racedata01.split("/")) == 2:
                race_time = racedata01.split("/")[0][:5]
                course = racedata01.split("/")[1]
            else:
                race_time = racedata01.split("/")[0][:5]
                course = racedata01.split("/")[1]
                weather = racedata01.split("/")[2].split(":")[1]
                course_condition = racedata01.split("/")[3].split(":")[1]
        else:
            race_name = self.driver.find_element_by_xpath(NK_LOCAL_RACE_NAME_XP).text
            race_info = self.driver.find_element_by_xpath(NK_LOCAL_RACE_COURSE_XP.format(1)).text
            race_cond1 = self.driver.find_element_by_xpath(NK_LOCAL_RACE_INFO_XP.format(1)).text
            race_cond2 = race_cond1[-3:]
            course = race_info.split("/")[0]
            race_time = race_info[-5:]
            weather = race_info.split("/")[1].split("：")[1]
            course_condition = race_info.split("/")[2].split("：")[1]

        header_text = [t.text.replace("\n", "") for t in self.driver.find_elements_by_xpath("//table[contains(concat(' ',normalize-space(@class),' '),' Shutuba_Table ')]/thead/tr[1]/th")]
        print(header_text)
        offset1 = 2 if race_status == "枠順確定" or race_status == "結果確定" else 0
        offset2 = 1 if not is_local else 0
        nk_horse_row_xp = "//a[contains(@href , '{}')]/../../../../../td[{}]" if not is_local \
            else "//a[contains(@href , '{}')]/../../td[{}]"
        nk_result_row_xp = "//a[contains(@href , '{}')]/../../../td[{}]"

        if "枠" in header_text:
            box_no_index = header_text.index("枠") + 1
            horse_no_index = header_text.index("馬番") + 1
            try:
                horse_no = self.driver.find_element_by_xpath(nk_horse_row_xp.format(horse_url[:-1], horse_no_index)).text
            except NoSuchElementException:
                horse_no = "00"
            try:
                box_no = self.driver.find_element_by_xpath(nk_horse_row_xp.format(horse_url[:-1], box_no_index)).text
            except NoSuchElementException:
                box_no = "0"

        if horse_no == "":
            horse_no = "00"
            box_no = "0"


        if "騎手" in header_text:
            jockey_index = header_text.index("騎手") + 1
            try:
                jockey = self.driver.find_element_by_xpath(nk_horse_row_xp.format(horse_url[:-1], jockey_index)).text
            except NoSuchElementException:
                jockey = None
        else:
            jockey = None

        if "人気" in header_text:
            pop_rank_index = header_text.index("人気") + 1
            odds_index = header_text.index("人気") - 1 + 1
            try:
                pop_rank = self.driver.find_element_by_xpath(nk_horse_row_xp.format(horse_url[:-1], pop_rank_index)).text
            except NoSuchElementException:
                pop_rank = None
            try:
                odds = self.driver.find_element_by_xpath(nk_horse_row_xp.format(horse_url[:-1], odds_index)).text
            except NoSuchElementException:
                odds = None
            if odds in ["除外", "取消"]:
                odds = 999.9
                pop_rank = 99
        else:
            pop_rank = None
            odds = None

        if "斤量" in header_text:
            burden_index = header_text.index("斤量") + 1
            try:
                burden = self.driver.find_element_by_xpath(nk_horse_row_xp.format(horse_url[:-1], burden_index)).text
            except NoSuchElementException:
                burden = None
        else:
            burden = None

        if "馬体重(増減)" in header_text:
            weight_index = header_text.index("馬体重(増減)") + 1
            try:
                weight = self.driver.find_element_by_xpath(nk_horse_row_xp.format(horse_url[:-1], weight_index)).text
            except NoSuchElementException:
                weight = None
        else:
            weight = None

        result, result_time, result_last3f, result_diff = "00", "0", "0", None
        result_url = None
        if race_status == "結果確定":
            result_url = race_url.replace("race_old", "race") + "&mode=result"
            time.sleep(self.seconds)
            self.driver.get(result_url)
            try:
                result = self.driver.find_element_by_xpath(nk_result_row_xp.format(horse_url[:-1], 1)).text.zfill(2)
            except NoSuchElementException:
                result = self.driver.find_element_by_xpath(nk_result_row_xp.format(horse_url[:-1], 9)).text
            try:
                result_time = self.driver.find_element_by_xpath(nk_result_row_xp.format(horse_url[:-1], 8)).text
            except NoSuchElementException:
                pass
            try:
                result_diff = self.driver.find_element_by_xpath(nk_result_row_xp.format(horse_url[:-1], 9)).text
                if result_diff in ["中止", "除外", "取消"]:
                    result = result_diff
            except NoSuchElementException:
                pass
            if not is_local:
                try:
                    result_last3f = self.driver.find_element_by_xpath(nk_result_row_xp.format(horse_url[:-1], 12)).text
                except NoSuchElementException:
                    pass
            else:
                try:
                    weight = self.driver.find_element_by_xpath(nk_result_row_xp.format(horse_url[:-1], 15)).text
                except NoSuchElementException:
                    pass

        training_result_list = self.get_training_result(int(horse_no), race_id, is_local)
        prediction_marks = self.get_predictions(horse_name, race_id, is_local)
        stable_comment = self.get_stable_comment(int(horse_no), race_id, is_local)

        return [race_time, race_name, course, race_cond2, horse_no, box_no, jockey, odds, pop_rank, result,
                result_url, training_result_list, prediction_marks, stable_comment, result_time, result_last3f, weather,
                course_condition, burden, weight, result_diff]

    def get_stable_comment(self, horse_no, race_id, is_local):
        if not is_local:
            try:
                self.driver.get(NK_STABLE_COMMENT_URL.format(race_id))
                time.sleep(self.seconds)
            except:
                return ""
        else:
            try:
                self.driver.get(NK_LOCAL_STABLE_COMMENT_URL.format(race_id))
                time.sleep(self.seconds)
            except:
                return ""

        if not self.driver.find_elements_by_xpath(NK_STABLE_COMMENT_XP):
            return ""

        stable_comment = ""
        stable_comment_columns = self.driver.find_elements_by_xpath(NK_STABLE_COMMENT_XP + "/tr[{}]/td"
                                                                    .format(horse_no + 1))
        markwk = self.driver.find_element_by_xpath('//*[@id="All_Comment_Table"]/tbody/tr[{}]/td[5]/span'
                    .format(horse_no + 1)).get_attribute("class")[-1:]
        if markwk == "1":
            mark = "◎"
        elif markwk == "2":
            mark = "○"
        elif markwk == "3":
            marrk = "△"
        else:
            mark = "―"
        stable_comment += stable_comment_columns[3].text + "【" + mark + "】"

        return stable_comment

    def get_predictions(self, horse_name, race_id, is_local):
        if not is_local:
            try:
                self.driver.get(NK_PREDICTIONS_URL.format(race_id))
                time.sleep(self.seconds)
            except:
                return ""
        else:
            try:
                self.driver.get(NK_LOCAL_PREDICTIONS_URL.format(race_id))
                time.sleep(self.seconds)
            except:
                return ""

        predictors_list = [t.text.replace("\n", "") for t in self.driver
                            .find_elements_by_xpath("//*[contains(@id,'yoso_goods_seq_')]")]
        table_rows = self.driver.find_elements_by_xpath("//dl[contains(@class,'Horse_Info')]/dd[1]/ul[1]/li")
        horse_names = [t.text for i, t in enumerate(table_rows)]
        horse_index = horse_names.index(horse_name)

        prediction_marks = ""
        for i, predictor in enumerate(predictors_list):
            if predictor == "CP予想":
                break

            if len(self.driver.find_elements_by_xpath
                    ("//*[contains(@id,'yoso_goods_seq_{}')]//span[contains(@class,'Icon_Shirushi')]"
                        .format(i))) == 0:
                continue

            mark_wk = \
                self.driver.find_element_by_xpath("//*[contains(@id,'yoso_goods_seq_{}')]/dd[1]/ul[1]/li[{}]/span[1]"
                                                  .format(i, horse_index + 1)).get_attribute("class")
            if mark_wk == "Icon_Shirushi Icon_Honmei":
                prediction_marks += "◎"
            elif mark_wk == "Icon_Shirushi Icon_Taikou":
                prediction_marks += "○"
            elif mark_wk == "Icon_Shirushi Icon_Kurosan":
                prediction_marks += "▲"
            elif mark_wk == "Icon_Shirushi Icon_Hoshi":
                prediction_marks += "☆"
            elif mark_wk == "Icon_Shirushi Icon_Osae":
                prediction_marks += "△"
            else:
                prediction_marks += "―"

        return prediction_marks

    def get_training_result(self, horse_no, race_id, is_local):
        training_result_list = []

        if not is_local:
            try:
                self.driver.get(NK_TRAINING_URL.format(race_id))
                time.sleep(self.seconds)
            except:
                training_result_list.append(["0000/00/00(火)", "", "", "", "", [], "", "", "", "", ""])
                return training_result_list
        else:
            try:
                self.driver.get(NK_LOCAL_TRAINING_URL.format(race_id))
                time.sleep(self.seconds)
            except:
                training_result_list.append(["0000/00/00(火)", "", "", "", "", [], "", "", "", "", ""])
                return training_result_list

        try:
            self.driver.find_element_by_link_text("中間の調教全て").click()
            time.sleep(self.seconds)
        except NoSuchElementException:
            pass

        try:
            training_table = self.driver.find_element_by_xpath(NK_TRAINING_XP)
        except NoSuchElementException:
            training_result_list.append(["0000/00/00(火)", "", "", "", "", [], "", "", "", "", ""])
            return training_result_list

        table_rows = self.driver.find_elements_by_xpath(NK_TRAINING_XP + "/tr/td[2]")
        horse_nos = [t.text for i, t in enumerate(table_rows)]
        horse_index = horse_nos.index(str(horse_no)) + 2
        try:
            num_of_trainings_wk = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td"
                                                                 .format(horse_index)).get_attribute("rowspan")
            if not num_of_trainings_wk:
                num_of_trainings = 1
            else:
                num_of_trainings = int(num_of_trainings_wk)
        except NoSuchElementException:
            num_of_trainings = 1

        for i in range(num_of_trainings):
            j = horse_index + i
            k = 0 if i == 0 else 3
            training_date = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]"
                                                                 .format(j, 5 - k)).text
            if training_date.split("/")[0] == "0000":
                training_result_list.append(["0000/00/00(火)", "", "", "", "", [], "", "", "", "", ""])
            else:
                training_course = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]"
                                                                 .format(j, 6 - k)).text
                training_course_condition = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]"
                                                                 .format(j, 7 - k)).text
                training_jockey = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]"
                                                                 .format(j, 8 - k)).text
                training_time_list = [t.text for t in self.driver.find_elements_by_xpath(NK_TRAINING_XP
                                                    + "/tr[{}]/td[{}]/ul/li".format(j, 9 - k))]
                training_time_grade_list = []
                for n in range(len(training_time_list)):
                    training_time_grade_wk = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]/ul/li[{}]"
                                                                        .format(j, 9 - k, n + 1)).get_attribute('class')
                    if training_time_grade_wk == "TokeiColor01":
                        training_time_grade = "**"
                    elif training_time_grade_wk == "TokeiColor02":
                        training_time_grade = "*"
                    else:
                        training_time_grade = ""
                    training_time_grade_list.append(training_time_grade)
                training_result_texts_list = [t.text for t in self.driver.find_elements_by_xpath(NK_TRAINING_XP
                                                    + "/tr[{}]/td[{}]//p".format(j, 9 - k))]
                training_position = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]"
                                                                      .format(j, 10 - k)).text
                training_stride = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]"
                                                                        .format(j, 11 - k)).text
                training_eval_text = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]"
                                                                       .format(j, 12 - k)).text
                training_eval_rank = self.driver.find_element_by_xpath(NK_TRAINING_XP + "/tr[{}]/td[{}]"
                                                                       .format(j, 13 - k)).text
                training_result_list.append([training_date, training_course, training_course_condition, training_jockey,
                                             training_time_list, training_result_texts_list, training_position,
                                             training_stride, training_eval_text, training_eval_rank,
                                             training_time_grade_list])
        return training_result_list

    def get_race_horse_list(self, is_sp_reg, is_past_result):
        time.sleep(self.seconds)
        race_horse_list_short = []
        self.driver.get(NK_BM_URL)
        if is_past_result:
            try:
                self.driver.find_element_by_xpath(NK_BM_PREVIOUS_WEEK_XP).click()
            except NoSuchElementException:
                pass
        is_local = False
        h = 1

        while True:
            i, j, k = 1, 1, 1
            if h > 1:
                if is_sp_reg:
                    try:
                        self.driver.find_element_by_xpath(NK_BM_NEXT_WEEK_XP).click()
                    except NoSuchElementException:
                        break
                elif not is_local:
                    is_local = True
                    try:
                        self.driver.find_element_by_xpath(NK_BM_LOCAL_XP).click()
                    except NoSuchElementException:
                        break
                else:
                    try:
                        self.driver.find_element_by_xpath(NK_BM_NEXT_DAY_XP).click()
                    except NoSuchElementException:
                        break

            while True:
                if is_local and i > 1:
                    break
                j, k = 1, 1
                if not is_local:
                    try:
                        race_mmdd_jpn = self.driver.find_element_by_xpath(NK_BM_DATE_XP.format(i + 2)).text
                    except NoSuchElementException:
                        break
                else:
                    try:
                        race_mmdd_jpn = self.driver.find_element_by_xpath(NK_BM_LOCAL_DATE_XP).text
                    except NoSuchElementException:
                        break
                if not is_local:
                    race_month = int(race_mmdd_jpn.split("月")[0])
                else:
                    race_month = int(race_mmdd_jpn.split("年")[1].split("月")[0])
                race_day = int(race_mmdd_jpn.split("月")[1].split("日")[0])
                race_weekday = race_mmdd_jpn.split("（")[1].split("）")[0]
                while True:
                    k = 1
                    if not is_local:
                        try:
                            race_url = self.driver.find_element_by_xpath(NK_BM_RACE_XP.format(i + 2, j))\
                                .get_attribute("href")
                        except NoSuchElementException:
                            break
                    else:
                        try:
                            race_url = self.driver.find_element_by_xpath(NK_BM_LOCAL_RACE_XP.format(j)).get_attribute(
                                "href")
                        except NoSuchElementException:
                            break
                    if not is_local:
                        try:
                            race_status = self.driver.find_element_by_xpath(NK_BM_STATE_XP.format(i + 2, j)).text
                        except NoSuchElementException:
                            break
                    else:
                        try:
                            race_status = self.driver.find_element_by_xpath(NK_BM_LOCAL_STATE_XP.format(j)).text
                        except NoSuchElementException:
                            break
                    if is_sp_reg and race_status != "特別登録" or not is_sp_reg and race_status == "特別登録":
                        j += 1
                        continue
                    if not is_local:
                        try:
                            race_grade = self.driver.find_element_by_xpath(NK_BM_GRADE_XP.format(i + 2, j)).text
                        except NoSuchElementException:
                            race_grade = None
                    else:
                        try:
                            race_grade = self.driver.find_element_by_xpath(NK_BM_LOCAL_GRADE_XP.format(j)).text
                        except NoSuchElementException:
                            race_grade = None
                    if not is_local:
                        try:
                            track_and_race_no = self.driver.find_element_by_xpath(NK_BM_CS_RN_XP.format(i + 2, j)).text
                        except NoSuchElementException:
                            break
                    else:
                        try:
                            track_and_race_no = self.driver.find_element_by_xpath(NK_BM_LOCAL_CS_RN_XP.format(j)).text
                        except NoSuchElementException:
                            break
                    track = track_and_race_no[0:2]
                    race_no = ("0" + track_and_race_no[2:])[-3:]
                    race_id = race_url.split("=")[2][1:] if is_local else race_url.split("=")[-1][0:]
                    race_year = int(race_id[0:4])
                    while True:
                        if not is_local:
                            try:
                                horse_url = self.driver.find_element_by_xpath(NK_BM_HORSE_XP.format(i + 2, j, k))\
                                    .get_attribute("href")
                            except NoSuchElementException:
                                break
                        else:
                            try:
                                horse_url = self.driver.find_element_by_xpath(NK_BM_LOCAL_HORSE_XP.format(j, k))\
                                    .get_attribute("href")
                            except NoSuchElementException:
                                break
                        horse_id = horse_url[-11:-1]
                        if not is_local:
                            try:
                                horse_name = self.driver.find_element_by_xpath(NK_BM_HORSE_XP.format(i + 2, j, k)).text
                            except NoSuchElementException:
                                break
                        else:
                            try:
                                horse_name = self.driver.find_element_by_xpath(NK_BM_LOCAL_HORSE_XP.format(j, k)).text
                            except NoSuchElementException:
                                break
                        race_horse_list_short.append([race_year, race_month, race_day, race_weekday, track, race_id,
                                                      race_grade, race_no, race_status, horse_id,
                                                      horse_url, horse_name, is_local])
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
