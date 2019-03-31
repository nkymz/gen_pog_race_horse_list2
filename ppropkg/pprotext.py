# -*- coding: utf-8 -*-

import os

NK_HORSE_URL_HEAD = "http://db.netkeiba.com/horse/"

POH_STATUS_HTML_HEADER = """
<head>
<link rel="stylesheet" type="text/css" href="style.css">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<p class="center">JRAホームページより取得した情報をもとに機械的に判定しているため、実際とは異なることがあります。</p>
"""

POH_STATUS_HTML_UPDATED_HEADER = """
<p>JRAホームページより取得した情報をもとに機械的に判定しているため、実際とは異なることがあります。<br>
全頭リストは<a href="https://nkymz.github.io/ppro_status_list/">こちら</a></p>
"""

COLLAPSE_HTML_RACE_RESULT = """
<div onclick="obj=document.getElementById('{}{}').style; obj.display=(obj.display=='none')?'block':'none';">
<a style="cursor:pointer;"><span style="border: 1px solid; background-color:#808080; color:#ffffff;">結果を見る
</span></a><br></div>
<div id="{}{}" style="display:none;clear:both;">
{}
</div>
"""
COLLAPSE_HTML_TRAINING = """
<div onclick="obj=document.getElementById('{}{}training').style; obj.display=(obj.display=='none')?'block':'none';">
<a style="cursor:pointer;"><span style="border: 1px solid; background-color:#808080; color:#ffffff;">調教を見る
</span></a><br></div>
<div id="{}{}training" style="display:none;clear:both;">
{}
</div>
"""


class POHStatusHTMLUpdated:

    def __init__(self):
        self.path = os.getenv("HOMEDRIVE", "None") + os.getenv("HOMEPATH", "None") + "/Dropbox/POG/"
        self.htmlpath = (self.path + "POH_status_list_updated.html").replace("\\", "/")
        self.f = open(self.htmlpath, mode="w")

    def close(self):
        self.f.close()

    @staticmethod
    def _get_horse_url(horse_id):
        return NK_HORSE_URL_HEAD + str(horse_id) + "/"

    def write_header(self):
        self.f.write(POH_STATUS_HTML_UPDATED_HEADER)

    def write_content_row(self, row):
        horse_name, owner_gender_rank, horse_id, status, status_old = row
        s = '<a href="' + self._get_horse_url(horse_id) + '">' + horse_name + owner_gender_rank + '</a>' + " " \
            + status_old + "→" + status + '<br>\n'
        self.f.write(s)


class RHListHTML:

    def __init__(self):
        self.path = os.getenv("HOMEDRIVE", "None") + os.getenv("HOMEPATH", "None") + "/Dropbox/POG/"
        self.htmlpath = (self.path + "PO_race_horse_list.html").replace("\\", "/")
        self.f = open(self.htmlpath, mode="w", encoding="utf-8")

    @staticmethod
    def _append_last3f(result_last3f):
        if result_last3f:
            return "(" + result_last3f + ")<br>"
        else:
            return "<br>"

    def close(self):
        self.f.close()

    def write_race_date(self, prev_date, race_date):
        s = '<h4>' + race_date + '</h4>\n'
        if prev_date is None:
            self.f.write(s)
        elif race_date != prev_date:
            self.f.write('</ul></li></ul>' + s)

    def write_race_info(self, race_url, track, race_no, race_name, status, weather, race_time, course, race_cond2,
                        course_condition, prev_date, race_date, prev_race_no, prev_race_time, prev_track, race_grade):
        race_name = race_name + "(" + race_grade + ")" if race_grade != "" else race_name
        s = '<li> <a href="' + race_url + '">' + track + race_no + " " + race_name + "【" + status + "】" \
            + '</a><br />\n'
        if weather == "&nbsp;":
            s2 = race_time + " " + course + " " + race_cond2 + '<br />\n<ul style="margin-left:-1em;">'
        else:
            s2 = race_time + " " + course + " " + race_cond2 + " " + weather + course_condition \
                 + '<br />\n<ul style="margin-left:-1em;">'
        if prev_date is None or (prev_date is not None and race_date != prev_date):
            self.f.write('<ul style="margin-left:-1em;">' + s)
            self.f.write(s2)
        elif race_date + race_no + race_time + track != prev_date + prev_race_no + prev_race_time + prev_track:
            self.f.write('</ul></li>' + s)
            self.f.write(s2)

    def write_horse_info(self, horse_no, waku, horse_url, horse_name, is_seal, jockey, owner, burden, weight):
        if horse_no != "00":
            s1 = '<li>' + waku + str(horse_no) + " " + '<a href="' + horse_url + '">'
        else:
            s1 = '<li> <a href="' + horse_url + '">'
        s2 = '<s>' + horse_name + '</s>' if is_seal else horse_name
        s3 = " " + jockey if jockey else ""
        s3 += " " + burden if burden else ""
        s3 += " " + weight if weight else ""
        self.f.write(s1 + s2 + owner + '</a>' + s3 + '<br />\n')

    def write_origin(self, origin):
        self.f.write(origin + '<br />\n')

    def write_horse_result(self, result, result_time, result_last3f, race_id, horse_id, race_grade):
        if result == "01":
            s1 = '<span style="font-weight: 900; color:#FF0000;">1着</span>' + " " + result_time \
                 + self._append_last3f(result_last3f)
        elif race_grade and result == "02" and race_grade[0] == "G":
            s1 = '<span style="font-weight: 700; color:#0000FF;">2着</span>' + " " + result_time \
                 + self._append_last3f(result_last3f)
        elif result in ["中止", "除外", "取消"]:
            s1 = result + "<br>"
        elif result != "00":
            s1 = result.lstrip("0") + '着' + " " + result_time + self._append_last3f(result_last3f)
        else:
            s1 = ""
        if s1 != "":
            self.f.write(COLLAPSE_HTML_RACE_RESULT.format(race_id, horse_id, race_id, horse_id, s1))

    def write_odds(self, odds, pop_rank, prediction_marks):
        if odds:
            self.f.write(str(odds) + '倍' + " " + str(pop_rank) + '番人気' + " " + prediction_marks + '<br />\n')

    def write_stable_comment(self, stable_comment):
        if stable_comment != "":
            self.f.write(stable_comment + "<br />\n")

    def write_training_result(self, training_result_list, race_id, horse_id):
        s = '<table border="1">'
        for training_result_row in training_result_list:
            training_date, training_course, training_course_condition, training_jockey, training_time_list, \
                training_result_texts_list, training_position, training_stride, training_eval_text, training_eval_rank \
                = training_result_row
            if training_date[:4] != "0000":
                s += "<tr><td>" + training_jockey + " " + training_date.split("/")[1] + "/" \
                     + training_date.split("/")[2].split("(")[0] + " " + training_course + " " \
                     + training_course_condition + " " + training_stride + " " + "<br />\n"
                for t in training_time_list:
                    s += t + " " if t != "-" else ""
                s += "[" + training_position + "]" + "<br />\n" if training_position else "<br />\n"
                for t in training_result_texts_list:
                    s += t + "<br>\n"
                s += training_eval_text + training_eval_rank + "<br /></td><tr>\n"
        if s != '<table border="1">':
            s += "</table>"
            self.f.write(COLLAPSE_HTML_TRAINING.format(race_id, horse_id, race_id, horse_id, s))
        self.f.write('</li>\n')

    def write_footer(self, date_time_now):
        self.f.write('</ul></li></ul><p>' + date_time_now + ' 時点の情報より作成</p>\n')


class POHStatusHTML:

    def __init__(self):
        self.path = os.getenv("HOMEDRIVE", "None") + os.getenv("HOMEPATH", "None") + "/Dropbox/POG/ppro_status_list/"
        self.htmlpath = (self.path + "index.html").replace("\\", "/")
        self.f = open(self.htmlpath, mode="w", encoding="utf-8")

    def close(self):
        self.f.close()

    @staticmethod
    def _get_horse_url(horse_id):
        return NK_HORSE_URL_HEAD + str(horse_id) + "/"

    def write_header(self, date_time):
        s = POH_STATUS_HTML_HEADER
        s += '<p class="right">' + date_time + ' 現在' + '</p>\n'
        s += '<table>\n'
        s += '<tr><th>オーナー</th><th>性別</th><th>順位</th><th>馬名</th><th>状況</th></tr>\n'
        self.f.write(s)

    def write_footer(self):
        self.f.write('</table>\n')

    def write_content_row(self, row):
        owner, gender, nom_rank, horse_name, horse_id, status, status_old = row
        if gender == "牡" and nom_rank == "1":
            s = '<tr><td rowspan="10">' + owner + '</td>' + '<td rowspan="5">' + gender + '</td>' + '<td>' + nom_rank \
                + '</td>'
        elif gender == "牝" and nom_rank == "1":
            s = '<tr><td rowspan="5">' + gender + '</td>' + '<td>' + nom_rank + '</td>'
        else:
            s = '<tr><td>' + nom_rank + '</td>'
        s += '<td><a href="' + self._get_horse_url(horse_id) + '">' + horse_name + '</a></td>'
        if status == status_old:
            s += '<td>' + status + '</td></tr>\n'
        else:
            s += '<td><span class="bold_red">' + status + '←' + status_old + '</span></td></tr>\n'

        self.f.write(s)


def main():
    test = POHStatusHTMLUpdated()
    test.write_content_row(["a", "b", 1, "c", "d"])
    test.close()


if __name__ == "__main__":
    main()
