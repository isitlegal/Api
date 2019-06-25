# -*- coding:utf-8 -*-

from flask import Flask, request
from urllib.parse import unquote, quote_plus
from selenium import webdriver

app = Flask(__name__)

@app.route('/')
def hello_world():

    return 'IsItLegal?'

@app.route('/', methods = ['POST', 'GET'])
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
    printlaw(url, lawname, driver)
    html = driver.page_source
    driver.quit()

    return html

def printlaw(url, lawname, driver):

    elements = driver.find_elements_by_class_name("pgroup")

    print(url, end='\n\n')
    print(lawname)
    for element in elements:
        text = element.text
        if text[1] == '제' or text[2] == '부':
            print()
        print(text)

if __name__ == '__main__':
    Flask.run(app)
