#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import os
import time

SSO_ID = 'c302890'
SSO_PASSWORD = 'dnten#DTEN09'


def main():
    # argvs = sys.argv
    # if len(argvs) < 2:
    #     print('[usage]python log_will_format.py [input log] [output log]')
    #     sys.exit(0)

    browser = init()
    login_sso(browser)
    deinit(browser)


def login_sso(driver):
    FORM_ID = 'username'
    FORM_PASS = 'uid_password'
    BUTTON_LOGIN = 'uid_submit'

    driver.get('https://cws.local.denso-ten.com/cws/cws')

    # input SSO ID/PASS
    id = driver.find_element_by_id(FORM_ID)
    id.send_keys(SSO_ID)
    password = driver.find_element_by_id(FORM_PASS)
    password.send_keys(SSO_PASSWORD)
    login_button = driver.find_element_by_id(BUTTON_LOGIN)
    login_button.click()

    # # サイト内で他の画面に遷移させたければ
    # driver.get('画面遷移させたいURL')


def init():
    # OSの環境変数に、http_proxy, https_proxyがあるとselenium起動に失敗するため無効化
    # localhostへのアクセスに失敗している？
    os.environ['http_proxy'] = ''
    os.environ['https_proxy'] = ''

    # option = Options()
    # PROXY = 'http://proxy.local.denso-ten.com:8080'
    # option.add_argument('--proxy-server=%s' % PROXY)

    print('start getting driver')
    # driver = webdriver.Chrome(chrome_options=option)
    driver = webdriver.Chrome()
    return driver


def deinit(driver):
    driver.quit()


if __name__ == '__main__':
    main()
