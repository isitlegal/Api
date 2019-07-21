# -*- coding:utf-8 -*-

from flask import Flask, request, make_response
from urllib.parse import quote_plus
from selenium import webdriver
import json
from collections import OrderedDict

app = Flask(__name__)

delay = 0.2
framename = "lawService"
chromedriverDIR = 'chromedriver'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("disable-gpu")

@app.route('/')
def hello_world():

    return 'IsItLegal?'

@app.route('/법령', methods = ['POST', 'GET'])
def 법령():
    lawname = request.args.get('lawname')
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

    return make_response(json.dumps(json_data, ensure_ascii=False, indent='\t'))

@app.route('/행정규칙', methods = ['POST', 'GET'])
def 행정규칙():
    lawname = request.args.get('lawname')
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

    return make_response(json.dumps(json_data, ensure_ascii=False, indent='\t'))

@app.route('/자치법규', methods = ['POST', 'GET'])
def 자치법규():
    lawname = request.args.get('lawname')
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

    return make_response(json.dumps(json_data, ensure_ascii=False, indent='\t'))

@app.route('/신규법령', methods = ['POST', 'GET'])
def 신규법령():
    date = request.args.get('date')
    url = 'http://www.law.go.kr/calendarInfoP.do?calDt=' + date

    delay = 1

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

    return make_response(json.dumps(json_data, ensure_ascii=False, indent='\t'))

@app.route('/법령체계도', methods = ['POST', 'GET'])
def 법령체계도():
    lawname = request.args.get('lawname')
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

    return make_response(json.dumps(json_data, ensure_ascii=False, indent='\t'))

@app.route('/판례', methods = ['POST', 'GET'])
def 판례():
    lawname = request.args.get('lawname').split(',')[2]
    url = 'http://www.law.go.kr/' + quote_plus('판례') + '/(' + quote_plus(lawname) + ')'
    url = "".join(url.split('+'))

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.switch_to.frame(framename)
    driver.implicitly_wait(delay)

    text = driver.find_element_by_class_name("viewwrap").text.split('\n')

    json_data = OrderedDict()
    json_data["판례명"] = text[0]
    json_data["판시사함"] = text[3]
    json_data["판결요지"] = text[5]
    json_data["참조조문"] = text[7]
    json_data["참조판례"] = text[9]
    json_data["전문"] = {}
    json_data["전문"]["원고, 상고인"] = text[13]
    json_data["전문"]["피고, 피상고인"] = text[15]
    json_data["전문"]["원심판결"] = text[17]
    json_data["전문"]["주문"] = text[19]
    json_data["전문"]["이유"] = "\n".join(text[21:])

    return make_response(json.dumps(json_data, ensure_ascii=False, indent='\t'))

@app.route('/판례목록', methods = ['POST', 'GET'])
def 판례목록():
    lawname = request.args.get('lawname')
    url = 'http://www.law.go.kr/unSc.do?tabMenuId=tab77&section=licPrec&query=' + quote_plus(lawname)

    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get(url)
    driver.implicitly_wait(delay)

    temp = driver.find_element_by_class_name('result_area').text.split("\n")

    json_data = OrderedDict()
    json_data["판례목록"] = []

    for t in temp:
        if t[-1] == "]":
            json_data["판례목록"].append(t)

    driver.quit()

    return make_response(json.dumps(json_data, ensure_ascii=False, indent='\t'))

@app.route('/법령목록', methods = ['POST', 'GET'])
def 법령목록():
    pagenum = int(request.args.get('pagenum'))
    driver = webdriver.Chrome(chromedriverDIR, chrome_options=options)
    driver.get('https://github.com/isitlegal/Api/blob/master/getlaw_all/%EB%B2%95%EB%A0%B9%EB%AA%A9%EB%A1%9D.csv')
    start = (pagenum - 1) * 20 + 2
    end = start + 19

    json_data = OrderedDict()
    json_data["법령목록"] = []

    for law in range(start, end):
        temp = driver.find_element_by_id('LC' + str(law)).text.split()
        dic = {}
        dic["law_name"] = " ".join(temp[1:-3])
        dic["departure"] = temp[0]
        dic["announce_date"] = temp[-3]
        dic["start_date"] = temp[-2]
        json_data["법령목록"].append(dic)

    return make_response(json.dumps(json_data, ensure_ascii=False, indent='\t'))

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

    Flask.run(app, host='0.0.0.0', port=3000)
