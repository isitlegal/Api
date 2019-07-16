# -*- coding:utf-8 -*-

from flask import Flask, request, make_response
from urllib import unquote, quote_plus
from selenium import webdriver
import json
from collections import OrderedDict

app = Flask(__name__)

delay = 0.2
framename = "lawService"
chromedriverDIR = '../chromedriver'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("disable-gpu")

@app.route('/')
def hello_world():

    return 'IsItLegal?'

@app.route('/law', methods = ['POST', 'GET'])
def law():

    lawname =  request.query_string
    url = 'http://www.law.go.kr/' + u'법령'.encode('utf-8') + '/' + lawname.decode('utf-8').encode('utf-8')

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    lawcontent = printlaw(driver, "pgroup")
    action = driver.find_element_by_id('lsRvsDocInfo')
    action.click()
    printlaw(driver, "sbj02")
    change = printlaw(driver, "pgroup").split("<법제처 제공>".decode('utf-8'))

    driver.quit()

    json_data = OrderedDict()
    json_data["name"] = lawname
    json_data["content"] = lawcontent
    json_data["changereason"] = change[0]
    json_data["change"] = change[1]

    return make_response(json.dumps(json_data, ensure_ascii=False, encoding='cp949'))

@app.route('/rule', methods = ['POST', 'GET'])
def rule():

    lawname = request.query_string
    url = 'http://www.law.go.kr/' + u'행정규칙'.encode('utf-8') + '/' + lawname.decode('utf-8').encode('utf-8')

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
    url = 'http://www.law.go.kr/' + u'법령체계도'.encode('utf-8') + '/' + u'행정규칙'.encode('utf-8') + '/' + lawname.decode('utf-8').encode('utf-8')
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    temp = driver.find_elements_by_class_name('cya2nlB')

    relation = []
    for i in temp:
        relation.append(i.text)
    relation.append(relation[0] + " 시행령".decode('utf-8'))

    driver.quit()

    json_data = OrderedDict()
    json_data["name"] = lawname
    json_data["content"] = lawcontent
    json_data["change"] = change
    json_data["relation"] = relation

    return make_response(json.dumps(json_data, ensure_ascii=False, encoding='cp949'))

@app.route('/locallaw', methods = ['POST', 'GET'])
def locallaw():

    lawname = request.query_string
    url = 'http://www.law.go.kr/' + u'자치법규'.encode('utf-8') + '/' + lawname.decode('utf-8').encode('utf-8')

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

    return make_response(json.dumps(json_data, ensure_ascii=False, encoding='cp949'))

@app.route('/newlaw', methods = ['POST', 'GET'])
def newlaw():

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

    driver.quit()

    return make_response(json.dumps(json_data, ensure_ascii=False, encoding='cp949'))

@app.route('/lawtree', methods = ['POST', 'GET'])
def lawtree():
    lawname = request.query_string
    url = 'http://www.law.go.kr/' + u'법령체계도'.encode('utf-8') + '/' + u'법령'.encode('utf-8') + '/' + lawname.decode('utf-8').encode('utf-8')

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

    return make_response(json.dumps(json_data, ensure_ascii=False, encoding='cp949'))

@app.route('/precedent', methods = ['POST', 'GET'])
def precedent():
    lawname = request.query_string
    url = 'http://www.law.go.kr/' + u'판례'.encode('utf-8') + '/(' + lawname.decode('utf-8').encode('utf-8') + ')'
    # url = "".join(url.split('+'))

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    text = driver.find_element_by_class_name("viewwrap").text.split('\n')

    json_data = OrderedDict()
    json_data["name"] = text[0]
    json_data["details"] = text[3]
    json_data["argument"] = text[5]
    json_data["refsentence"] = text[7]
    json_data["refpreference"] = text[9]
    json_data["text"] = {}
    json_data["text"]["claimant"] = text[12]
    json_data["text"]["defendant"] = text[14]
    json_data["text"]["judgement"] = text[16]
    json_data["text"]["text"] = text[18]
    json_data["text"]["reason"] = "\n".join(text[20:])

    return make_response(json.dumps(json_data, ensure_ascii=False, encoding='cp949'))

@app.route('/precedents', methods = ['POST', 'GET'])
def precedents():
    lawname = request.query_string
    url = 'http://www.law.go.kr/unSc.do?tabMenuId=tab77&section=licPrec&query=' + lawname.decode('utf-8').encode('utf-8')

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.implicitly_wait(delay)

    temp = driver.find_element_by_class_name('result_area').text.split("\n")

    json_data = OrderedDict()
    json_data["precedentlist"] = []

    for t in temp:
        if t[-1] == "]":
            json_data["precedentlist"].append(t)

    driver.quit()

    return make_response(json.dumps(json_data, ensure_ascii=False, encoding='cp949'))

@app.route('/laws', methods = ['POST', 'GET'])
def laws():
    pagenum = int(unquote('http://www.law.go.kr/' + request.query_string.decode('utf-8'))[21:])
    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get('https://github.com/isitlegal/Api/blob/master/getlaw_all/%EB%B2%95%EB%A0%B9%EB%AA%A9%EB%A1%9D.csv')
    start = (pagenum - 1) * 20 + 2
    end = start + 19

    json_data = OrderedDict()
    json_data["laws"] = []

    for law in range(start, end):
        temp = driver.find_element_by_id('LC' + str(law)).text.split()
        temp = temp[0 : 1] + [" ".join(temp[1 : -3])] + temp[-3 : ]
        json_data["laws"].append(temp)

    return make_response(json.dumps(json_data, ensure_ascii=False, encoding='cp949'))

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
            if text[1] == '제'.decode('utf-8') or text[2] == '부'.decode('utf-8'):
                t += '\n\n'
            t += text + '\n'
        except:
            pass
    return t

def makejson(json_data, name, data):

    for i in range(len(data[0])):
        t = {"name" : data[0][i],
             "kind" : data[1][i],
             "number" : data[2][i],
             "departure" : data[3][i]}
        json_data[name].append(t)

    return json_data

if __name__ == '__main__':

    Flask.run(app, port=1937)