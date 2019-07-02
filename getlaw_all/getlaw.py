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

    driver.quit()

    json_data = OrderedDict()
    json_data["name"] = lawname
    json_data["content"] = lawcontent
    json_data["change"] = change

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
def getnewlaws():
    date = request.query_string.decode('utf-8')
    url = 'http://www.law.go.kr/calendarInfoP.do?calDt=' + date

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.implicitly_wait(delay)

    json_data = OrderedDict()
    json_data["시행법령"] = cleantext(driver.find_element_by_id('Si_tab').text)
    json_data["공포법령"] = cleantext(driver.find_element_by_id('Gong_tab').text)
    json_data["폐지법령"] = cleantext(driver.find_element_by_id('Abo_tab').text)
    json_data["한시법령"] = cleantext(driver.find_element_by_id('Han_tab').text)
    json_data["한시조문"] = cleantext(driver.find_element_by_id('Jo_tab').text)
    json_data["위헌조문"] = cleantext(driver.find_element_by_id('Voc_tab').text)

    driver.quit()

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

    res = []
    for law in zip(laws, kind, number, department):
        temp = {}
        temp["법령명"] = law[0]
        temp["구분"] = law[1]
        temp["공포번호"] = law[2]
        temp["소관부처"] = law[3]
        res.append(temp)

    return res

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

if __name__ == '__main__':
    Flask.run(app)


