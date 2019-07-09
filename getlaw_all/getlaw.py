# -*- coding:utf-8 -*-

from flask import Flask, request, make_response
from urllib.parse import unquote, quote_plus
from selenium import webdriver
import json
from collections import OrderedDict

app = Flask(__name__)

delay = 3
framename = "lawService"
chromedriverDIR = '../chromedriver'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("disable-gpu")

@app.route('/')
def hello_world():

    return 'IsItLegal?'

@app.route('/법령', methods = ['POST', 'GET'])
def 법령():

    lawname = unquote('http://www.law.go.kr/' + request.query_string.decode('utf-8'))[21:]
    url = 'http://www.law.go.kr/' + quote_plus('법령') + '/' + quote_plus(lawname)

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    lawcontent = printlaw(driver, "pgroup")
    action = driver.find_element_by_id('lsRvsDocInfo')
    action.click()
    printlaw(driver, "sbj02")
    change = printlaw(driver, "pgroup").split("<법제처 제공>")

    driver.quit()

    json_data = OrderedDict()
    json_data["name"] = lawname
    json_data["content"] = lawcontent
    json_data["changereason"] = change[0]
    json_data["change"] = change[1]

    return make_response(json.dumps(json_data, ensure_ascii=False))

@app.route('/행정규칙', methods = ['POST', 'GET'])
def 행정규칙():

    lawname = unquote('http://www.law.go.kr/' + request.query_string.decode('utf-8'))[21:]
    url = 'http://www.law.go.kr/' + quote_plus('행정규칙') + '/' + quote_plus(lawname)

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    lawcontent = printlaw(driver, "pgroup")
    action = driver.find_element_by_id('lsRvsDocInfo')
    action.click()
    printlaw(driver, "sbj02")
    change = printlaw(driver, "pgroup")

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    url = 'http://www.law.go.kr/' + quote_plus('법령체계도') + '/' + quote_plus('행정규칙') + '/' + quote_plus(lawname)
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    temp = driver.find_elements_by_class_name('cya2nlB')

    # relation = [law.text]
    relation = []
    for i in temp:
        relation.append(i.text)
    relation.append(relation[0] + " 시행령")

    driver.quit()

    json_data = OrderedDict()
    json_data["name"] = lawname
    json_data["content"] = lawcontent
    json_data["change"] = change
    json_data["relation"] = relation

    return make_response(json.dumps(json_data, ensure_ascii=False))

@app.route('/자치법규', methods = ['POST', 'GET'])
def 자치법규():

    lawname = unquote('http://www.law.go.kr/' + request.query_string.decode('utf-8'))[21:]
    url = 'http://www.law.go.kr/' + quote_plus('자치법규') + '/' + quote_plus(lawname)

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    lawcontent = printlaw(driver, "pgroup")
    action = driver.find_element_by_id('rvsDoc')
    action.click()
    printlaw(driver, "sbj02")
    change = printlaw(driver, "pgroup")

    driver.quit()

    json_data = OrderedDict()
    json_data["name"] = lawname
    json_data["content"] = lawcontent
    json_data["change"] = change

    return make_response(json.dumps(json_data, ensure_ascii=False))

@app.route('/신규법령', methods = ['POST', 'GET'])
def 신규법령():
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
    json_data["Si"] = []
    json_data["Gong"] = []
    json_data["Abo"] = []
    json_data["Han"] = []
    json_data["Jo"] = []
    json_data["Voc"] = []

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

    return make_response(json.dumps(json_data, ensure_ascii=False))

@app.route('/법령체계도', methods = ['POST', 'GET'])
def getlawtree():
    lawname = unquote('http://www.law.go.kr/' + request.query_string.decode('utf-8'))[21:]
    url = 'http://www.law.go.kr/' + quote_plus('법령체계도') + '/' + quote_plus('법령') + '/' + quote_plus(lawname)

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    temp = driver.find_elements_by_class_name('cya2nlB')
    json_data = OrderedDict()
    json_data["upper"] = []
    json_data["main"] = [lawname]
    json_data["lower"] = []

    for i in temp:
        if len(i.text) > len(lawname):
            json_data["lower"].append(i.text)
        else:
            json_data["upper"].append(i.text)

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
        department.append(law_split[-1])

    return [laws, kind, number, department]

def printlaw(driver, search):

    elements = driver.find_elements_by_class_name(search)

    t = ''

    for element in elements:
        text = element.text
        try:
            if text[1] == '제' or text[2] == '부':
                t += '\n\n'
            t += text + '\n'
        except:
            pass
    return t

def makejson(json_data, name, data):

    for i in range(len(data[0])):
        t = {"법령명" : data[0][i],
             "구분" : data[1][i],
             "공포번호" : data[2][i],
             "소관부처" : data[3][i]}
        json_data[name].append(t)

    return json_data

if __name__ == '__main__':
    Flask.run(app)
