# -*- coding: utf-8 -*-

import sys
import re
import datetime

from ppropkg.pproxls import POHorseList
from ppropkg.pprows import NetKeiba, SoupNK
from ppropkg.pprotext import RHListHTML


def get_stable_comment(horse_no, race_id, soup_nk):
    soup = soup_nk.get('http://race.netkeiba.com/?pid=race_old&id=' + "c" + race_id + '&mode=comment')

    if not soup.find("div", class_="race_comment_box"):
        return ""

    stable_comment = ""
    stable_comment_row = soup.find("div", class_="race_comment_box").find("table").find_all("tr")[horse_no]
    stable_comment_columns = stable_comment_row.find_all("td")
    stable_comment += stable_comment_columns[3].text + "【" + stable_comment_columns[4].text + "】"

    return stable_comment


def get_predictions(horse_name, race_id, soup_nk):
    soup = soup_nk.get('http://race.netkeiba.com/?pid=yoso&id=' + "c" + race_id)

    if not soup.find("div", id="race_main").find("table"):
        return ""

    prediction_header_text = [t.text for t in soup.find("div", id="race_main").find("table").find("tr").find_all("th")]
    hn_col_index = prediction_header_text.index("馬名")
    table_rows = soup.find("div", id="race_main").find("table").find_all("tr")
    horse_names = [t.find_all("td")[hn_col_index].text for i, t in enumerate(table_rows) if i > 0]
    horse_index = horse_names.index(horse_name) + 1
    predictions = soup.find("div", id="race_main").find("table").find_all("tr")[horse_index].find_all("td")
    if not predictions:
        return ""
    prediction_marks = ""
    if "\nCP予想\n" in prediction_header_text:
        range_max = prediction_header_text.index("\nCP予想\n")
    else:
        range_max = hn_col_index
    for i in range(2, range_max):
        prediction_marks += predictions[i].text.strip() if predictions[i].text.strip("\n") in "◎○▲☆△" else "□"
    return prediction_marks


def get_training_result(horse_no, race_id, soup_nk):
    training_result_list = []
    soup = soup_nk.get('http://race.netkeiba.com/?pid=race&id=' + "c" + race_id + '&mode=oikiri')

    if soup.find("a", href=re.compile("type=1")):
        target_url = 'http://race.netkeiba.com' + soup.find("a", href=re.compile("type=1")).get("href")
        soup = soup_nk.get(target_url)

    if not soup.find("div", id="race_main").find("table"):
        training_result_list.append(["0000/00/00(火)", "", "", "", "", [], "", "", "", ""])
        return training_result_list

    table_rows = soup.find("div", id="race_main").find("table").find_all("tr")
    horse_nos = [t.find_all("td")[1].text for i, t in enumerate(table_rows) if i > 0]
    horse_index = horse_nos.index(str(horse_no)) + 1

    training_result_row = table_rows[horse_index]
    if training_result_row.find("td").get("rowspan"):
        num_of_trainings = int(training_result_row.find("td").get("rowspan"))
    else:
        num_of_trainings = 1

    for i in range(num_of_trainings):
        columns_offset = 0 if i == 0 else 3
        training_result_row = table_rows[horse_index + i]
        training_result_columns = training_result_row.find_all("td")
        training_date = training_result_columns[3 - columns_offset].text
        if training_date.split("/")[0] == "0000":
            training_result_list.append(["0000/00/00(火)", "", "", "", "", [], "", "", "", ""])
        else:
            training_course = training_result_columns[4 - columns_offset].text
            training_course_condition = training_result_columns[5 - columns_offset].text
            training_jockey = training_result_columns[6 - columns_offset].text
            training_time_list = [t.text for t in training_result_columns[7 - columns_offset].find("ul").find_all("li")]
            training_result_texts_list = [t.text for t in training_result_columns[7 - columns_offset].find_all("p")]
            training_position = training_result_columns[8 - columns_offset].text
            training_stride = training_result_columns[9 - columns_offset].text
            training_eval_text = training_result_columns[10 - columns_offset].text
            training_eval_rank = training_result_columns[11 - columns_offset].text
            training_result_list.append([training_date, training_course, training_course_condition, training_jockey,
                                         training_time_list, training_result_texts_list, training_position,
                                         training_stride, training_eval_text, training_eval_rank])
    return training_result_list


def get_race_info(race_url, horse_url, race_status, soup_nk, race_id, horse_name):
    soup = soup_nk.get(race_url)
    h1_list = soup.find_all('h1')
    race_name = h1_list[1].text.strip()
    race_attrib_list = h1_list[1].find_all_next('p', limit=4)
    course = race_attrib_list[0].string.strip()
    race_time = race_attrib_list[1].string[-5:]
    weather = race_attrib_list[1].string.split("/")[0].split("：")[1]
    course_condition = race_attrib_list[1].string.split("/")[1].split("：")[1]
    race_cond1 = race_attrib_list[2].string
    race_cond2 = race_attrib_list[3].string

    horse_tag = soup.find("a", href=horse_url)
    horse_row = horse_tag.find_previous("tr")
    if not horse_row.find("td", class_="umaban"):
        horse_no = "00"
        box_no = "0"
    else:
        horse_no = horse_row.find("td", class_="umaban").string
        box_no = horse_row.find("td", class_=re.compile("^waku")).string
    if not horse_row.find_all('td', class_='txt_l', limit=2)[1].find('a'):
        jockey = None
    else:
        jockey = horse_row.find_all('td', class_='txt_l', limit=2)[1].find('a').string
    if not horse_row.find('td', class_='txt_r'):
        odds = None
        pop_rank = None
    else:
        odds = horse_row.find('td', class_='txt_r').string
        pop_rank = horse_row.find('td', class_='txt_r').find_next('td').string

    result, result_time, result_last3f = "00", "0", "0"
    result_url = None
    if race_status == "結果確定":
        result_url = race_url.replace("race_old", "race") + "&mode=result"
        soup = soup_nk.get(result_url)
        horse_tag = soup.find("a", href=horse_url)
        horse_row = horse_tag.find_previous("tr")
        if horse_row.find("td", class_="result_rank").string:
            result = horse_row.find("td", class_="result_rank").string.zfill(2)
        else:
            result = "99"
        result_time = horse_row.find_all("td")[7].string
        result = horse_row.find_all("td")[8].string if result == "99" else result
        result_last3f = horse_row.find_all("td")[11].string

    training_result_list = get_training_result(int(horse_no), race_id, soup_nk)
    prediction_marks = get_predictions(horse_name, race_id, soup_nk)
    stable_comment = get_stable_comment(int(horse_no), race_id, soup_nk)

    return [race_time, race_name, course, race_cond1, race_cond2, horse_no, box_no, jockey, odds, pop_rank, result,
            result_url, training_result_list, prediction_marks, stable_comment, result_time, result_last3f, weather,
            course_condition]


def get_waku(box_no):
    if box_no == "1":
        waku = '<span style="border: 1px solid; background-color:#ffffff; color:#000000;">1</span> '
    elif box_no == "2":
        waku = '<span style="border: 1px solid; background-color:#000000; color:#ffffff;">2</span> '
    elif box_no == "3":
        waku = '<span style="border: 1px solid; background-color:#ff0000; color:#ffffff;">3</span> '
    elif box_no == "4":
        waku = '<span style="border: 1px solid; background-color:#0000ff; color:#ffffff;">4</span> '
    elif box_no == "5":
        waku = '<span style="border: 1px solid; background-color:#ffff00; color:#000000;">5</span> '
    elif box_no == "6":
        waku = '<span style="border: 1px solid; background-color:#00ff00; color:#ffffff;">6</span> '
    elif box_no == "7":
        waku = '<span style="border: 1px solid; background-color:#ff8000; color:#000000;">7</span> '
    elif box_no == "8":
        waku = '<span style="border: 1px solid; background-color:#ff8080; color:#000000;">8</span> '
    else:
        waku = None
    return waku


def write_html(race_horse_list, date_time_now):
    rhl_html = RHListHTML()
    prev_date = None
    prev_race_no = None
    prev_race_time = None
    prev_track = None

    for race_horse in race_horse_list:
        sort_key, race_date, race_time, track, race_no, race_name, race_grade, course, race_cond1, race_cond2, \
            horse_no, box_no, horse_name, jockey, odds, pop_rank, race_url, horse_url, owner, origin, result, \
            race_status, is_seal, result_url, training_result_list, prediction_marks, stable_comment, result_time, \
            result_last3f, weather, course_condition, race_id, horse_id \
            = race_horse
        waku = get_waku(box_no)
        race_url = result_url if race_status == "結果確定" else race_url

        rhl_html.write_race_date(prev_date, race_date)
        rhl_html.write_race_info(race_url, track, race_no, race_name, race_status, weather, race_time, course,
                                 race_cond2, course_condition, prev_date, race_date, prev_race_no, prev_race_time,
                                 prev_track, race_grade)
        rhl_html.write_horse_info(horse_no, waku, horse_url, horse_name, is_seal, jockey, owner)
        rhl_html.write_origin(origin)
        rhl_html.write_horse_result(result, result_time, result_last3f, race_id, horse_id, race_grade)
        rhl_html.write_odds(odds, pop_rank, prediction_marks)
        rhl_html.write_stable_comment(stable_comment)
        rhl_html.write_training_result(training_result_list, race_id, horse_id)

        prev_date = race_date
        prev_race_no = race_no
        prev_race_time = race_time
        prev_track = track

    rhl_html.write_footer(date_time_now)
    rhl_html.close()


def main():
    args = sys.argv
    is_sp_reg = True if len(args) > 1 and args[1] == "sp" else False
    is_sp_reg = True
    mynow = datetime.datetime.today()
    date_time_now = mynow.strftime("%Y/%m/%d %H:%M:%S")
    race_horse_list = []
    poh_list = POHorseList()
    nk_id, nk_pw = poh_list.get_nk_auth_info()
    nk = NetKeiba(nk_id, nk_pw, 1, "headless")
    soup_nk = SoupNK("lxml", 1, nk_id, nk_pw)

    for rhl_short in nk.get_race_horse_list(is_sp_reg):
        race_year, race_month, race_day, race_weekday, track, race_id, race_grade, race_no,\
            race_status, horse_id, horse_url, horse_name = rhl_short
        owner, origin, is_seal = poh_list.get_a_horse(horse_id, "ogr", "origin", "seal")
        race_url = 'http://race.netkeiba.com/?pid=race_old&id=' + "c" + race_id
        race_time, race_name, course, race_cond1, race_cond2, horse_no, box_no, jockey, odds, pop_rank, result, \
            result_url, training_result_list, prediction_marks, stable_comment, result_time, result_last3f, weather, \
            course_condition = get_race_info(race_url, horse_url, race_status, soup_nk, race_id, horse_name)
        race_date = str(race_year) + "/" + str(race_month).zfill(2) + "/" + str(race_day).zfill(2) + "(" \
            + race_weekday + ")"
        sort_key = race_date + race_time + race_no + track + horse_no.zfill(2) + horse_name
        race_horse_list.append(
                [sort_key, race_date, race_time, track, race_no, race_name, race_grade, course.replace("\xa0", " "),
                 race_cond1, race_cond2.replace("\xa0", " "), horse_no, box_no, horse_name, jockey, odds, pop_rank,
                 race_url, horse_url, owner, origin, result, race_status, is_seal, result_url, training_result_list,
                 prediction_marks, stable_comment, result_time, result_last3f, weather, course_condition, race_id,
                 horse_id])
    nk.quit()
    poh_list.close()
    race_horse_list.sort()

    write_html(race_horse_list, date_time_now)


if __name__ == "__main__":
    main()
