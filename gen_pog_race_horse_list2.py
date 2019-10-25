# -*- coding: utf-8 -*-

import sys
#import re
import datetime
import pprint

from ppropkg.pproxls import POHorseList
from ppropkg.pprows import NetKeiba, SoupNK
from ppropkg.pprotext import RHListHTML


def get_stable_comment(horse_no, race_id, soup_nk):
    soup = soup_nk.get('http://race.netkeiba.com/?pid=race_old&id=' + "c" + race_id + '&mode=comment', "ignore_euc-jp")

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
            result_last3f, weather, course_condition, race_id, horse_id, burden, weight, result_diff \
            = race_horse
        waku = get_waku(box_no)
        race_url = result_url if race_status == "結果確定" else race_url

        rhl_html.write_race_date(prev_date, race_date)
        rhl_html.write_race_info(race_url, track, race_no, race_name, race_status, weather, race_time, course,
                                 race_cond2, course_condition, prev_date, race_date, prev_race_no, prev_race_time,
                                 prev_track, race_grade)
        rhl_html.write_horse_info(horse_no, waku, horse_url, horse_name, is_seal, jockey, owner, burden, weight)
        rhl_html.write_origin(origin)
        rhl_html.write_horse_result(result, result_time, result_last3f, race_id, horse_id, race_grade, result_diff)
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
    mynow = datetime.datetime.today()
    date_time_now = mynow.strftime("%Y/%m/%d %H:%M:%S")
    race_horse_list = []
    poh_list = POHorseList()
    nk_id, nk_pw = poh_list.get_nk_auth_info()
    nk = NetKeiba(nk_id, nk_pw, 0, "test")
#    soup_nk = SoupNK("html5lib", 1, nk_id, nk_pw)

    for rhl_short in nk.get_race_horse_list(is_sp_reg):
        race_year, race_month, race_day, race_weekday, track, race_id, race_grade, race_no,\
            race_status, horse_id, horse_url, horse_name, is_local = rhl_short
        owner, origin, is_seal = poh_list.get_a_horse(horse_id, "ogr", "origin", "seal")
        if not is_local:
            race_url = 'http://race.netkeiba.com/?pid=race_old&id=' + "c" + race_id
        else:
            race_url = 'http://nar.netkeiba.com/?pid=race_old&id=' + "c" + race_id
        race_time, race_name, course, race_cond1, race_cond2, horse_no, box_no, jockey, odds, pop_rank, result, \
            result_url, training_result_list, prediction_marks, stable_comment, result_time, result_last3f, weather, \
            course_condition, burden, weight, result_diff \
            = nk.get_race_detail(race_url, horse_url, race_status, race_id, horse_name, is_local, race_status)
        race_date = str(race_year) + "/" + str(race_month).zfill(2) + "/" + str(race_day).zfill(2) + "(" \
            + race_weekday + ")"
        sort_key = race_date + race_time + race_no + track + horse_no.zfill(2) + horse_name
        race_horse_list.append(
                [sort_key, race_date, race_time, track, race_no, race_name, race_grade, course.replace("\xa0", " "),
                 race_cond1, race_cond2.replace("\xa0", " "), horse_no, box_no, horse_name, jockey, odds, pop_rank,
                 race_url, horse_url, owner, origin, result, race_status, is_seal, result_url, training_result_list,
                 prediction_marks, stable_comment, result_time, result_last3f, weather, course_condition, race_id,
                 horse_id, burden, weight, result_diff])
    nk.quit()
    poh_list.close()
    race_horse_list.sort()
    pprint.pprint(race_horse_list)
    write_html(race_horse_list, date_time_now)


if __name__ == "__main__":
    main()
