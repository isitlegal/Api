# -*- coding:utf-8 -*-

from flask import Flask, request, make_response
from selenium import webdriver
import json
from collections import OrderedDict

app = Flask(__name__)

@app.route('/')
def hello_world():

    return 'IsItLegal?'

@app.route('/newlaw', methods = ['POST', 'GET'])
def getnewlaws():
    date = request.query_string.decode('utf-8')
    url = 'http://www.law.go.kr/calendarInfoP.do?calDt=' + date

    delay = 3
    chromedriverDIR = '../chromedriver'

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.implicitly_wait(delay)

    json_data = OrderedDict()
    json_data["data"] = []
    json_data["data"].append({"분류": "시행법령"})
    appendlaw(json_data, cleantext(driver.find_element_by_id('Si_tab').text))
    json_data["data"].append({"분류": "공포법령"})
    appendlaw(json_data, cleantext(driver.find_element_by_id('Gong_tab').text))
    json_data["data"].append({"분류": "폐지법령"})
    appendlaw(json_data, cleantext(driver.find_element_by_id('Abo_tab').text))
    json_data["data"].append({"분류": "한시법령"})
    appendlaw(json_data, cleantext(driver.find_element_by_id('Han_tab').text))
    json_data["data"].append({"분류": "한시조문"})
    appendlaw(json_data, cleantext(driver.find_element_by_id('Jo_tab').text))
    json_data["data"].append({"분류": "위헌조문"})
    appendlaw(json_data, cleantext(driver.find_element_by_id('Voc_tab').text))

    html = driver.page_source
    driver.quit()

    with open(date + ".json", "w", encoding="utf-8") as make_json:
        json.dump(json_data, make_json, ensure_ascii=False, indent="\t")

    return make_response(json.dumps(json_data, ensure_ascii=False))

def cleantext(text):
    text = text.split('\n')
    text = text[1:]
    laws = []
    kind = []
    number = []
    department = []
    for law in text:
        law_split = law.split()
        laws.append(' '.join(law_split[:-3]))
        kind.append(law_split[-3])
        number.append(law_split[-2])
        department.append(law_split[-1])

    # return [laws, kind, number, department]

    res = []
    for law in zip(laws, kind, number, department):
        temp = {}
        temp["법령명"] = law[0]
        temp["구분"] = law[1]
        temp["공포번호"] = law[2]
        temp["소관부처"] = law[3]
        res.append(temp)

    return res

def appendlaw(json, laws):
    for law in laws:
        json["data"].append(law)
    return json

if __name__ == '__main__':
    Flask.run(app)
