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

@app.route('/law', methods = ['POST', 'GET'])
def inputTest():

    lawname = unquote('http://www.law.go.kr/' + request.query_string.decode('utf-8'))[21:]
    url = 'http://www.law.go.kr/' + quote_plus('법령') + '/' + quote_plus(lawname)
    delay = 3
    framename = "lawService"
    chromedriverDIR = 'chromedriver'

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")

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
