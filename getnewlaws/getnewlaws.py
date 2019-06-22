# -*- coding:utf-8 -*-

from flask import Flask, request, make_response
from urllib.parse import unquote, quote_plus
from selenium import webdriver
import json
from collections import OrderedDict

app = Flask(__name__)

@app.route('/')
def hello_world():

    return 'IsItLegal?'

@app.route('/신규법령', methods = ['POST', 'GET'])
def inputTest():
    date = request.query_string.decode('utf-8')
    url = 'http://www.law.go.kr/calendarInfoP.do?calDt=' + date

    delay = 3
    chromedriverDIR = 'chromedriver'
    law_kinds = ['Si_tab', 'Gong_tab', 'Abo_tab', 'Han_tab', 'Jo_tab', 'Voc_tab']

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.implicitly_wait(delay)

    json_data = OrderedDict()
    json_data["Si"] = {}
    json_data["Gong"] = {}
    json_data["Abo"] = {}
    json_data["Han"] = {}
    json_data["Jo"] = {}
    json_data["Voc"] = {}

    Si = cleantext(driver.find_element_by_id('Si_tab').text)
    json_data = makejson(json_data, "Si", Si)
    Gong = cleantext(driver.find_element_by_id('Gong_tab').text)
    json_data = makejson(json_data, "Gong", Gong)
    Abo = cleantext(driver.find_element_by_id('Abo_tab').text)
    json_data = makejson(json_data, "Abo", Abo)
    Han = cleantext(driver.find_element_by_id('Han_tab').text)
    json_data = makejson(json_data, "Han", Han)
    Jo = cleantext(driver.find_element_by_id('Jo_tab').text)
    json_data = makejson(json_data, "Jo", Jo)
    Voc = cleantext(driver.find_element_by_id('Voc_tab').text)
    json_data = makejson(json_data, "Voc", Voc)
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
        laws.append(" ".join(law_split[:-3]))
        kind.append(law_split[-3])
        number.append(law_split[-2])
        department.append(law_split[-1].split(','))

    return [laws, kind, number, department]

def makejson(json_data, name, data):
    json_data[name]["법령명"] = data[0]
    json_data[name]["구분"] = data[1]
    json_data[name]["공포번호"] = data[2]
    json_data[name]["소관부처"] = data[3]

    return json_data

if __name__ == '__main__':
    Flask.run(app)
