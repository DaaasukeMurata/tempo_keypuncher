#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge import service as fs
# from selenium.webdriver.chrome.options import Options
import chromedriver_binary  # need to run 'pip install chromedriver-binary-auto'
import os
import time
import json


class AttendanceInfo:

    def __init__(self):
        self.driver = self._get_driver(browser_type='edge')
        # setting data
        self.SSO_ID = ''
        self.SSO_PASS = ''
        self._load_setting()    # load settings
        self._login_sso()

    def __del__(self):
        self.driver.quit()

    # load settings from ""./setting.json"
    def _load_setting(self):
        with open('./setting.json') as setting_file:
            settings = json.load(setting_file)
            self.SSO_ID = settings['SSO_ID']
            self.SSO_PASS = settings['SSO_PASS']

    def _get_driver(self, browser_type='edge'):
        # OSの環境変数に、http_proxy, https_proxyがあるとselenium起動に失敗するため無効化
        # localhostへのアクセスに失敗している？
        os.environ['http_proxy'] = ''
        os.environ['https_proxy'] = ''

        # browser_typeに応じたdriverの取得
        driver = None
        browser = browser_type.lower()
        if browser == 'edge':
            edge_service = fs.Service(executable_path='./msedgedriver.exe')
            driver = webdriver.Edge(service=edge_service)
        elif browser == 'chrome':
            driver = webdriver.Chrome()
        else:
            print('ERROR: browser_type : ', browser_type, ' is invalid.')
        return driver

    def _login_sso(self):
        SSO_URL = 'https://cws.local.denso-ten.com/cws/cws'
        FORM_ID = 'username'
        FORM_PASS = 'uid_password'
        BUTTON_LOGIN = 'uid_submit'

        self.driver.get(SSO_URL)

        # input SSO ID/PASS
        id = self.driver.find_element(by=By.ID, value=FORM_ID)
        id.send_keys(self.SSO_ID)
        password = self.driver.find_element(by=By.ID, value=FORM_PASS)
        password.send_keys(self.SSO_PASS)
        login_button = self.driver.find_element(by=By.ID, value=BUTTON_LOGIN)
        login_button.click()


def main():
    # argvs = sys.argv
    # if len(argvs) < 2:
    #     print('[usage]python log_will_format.py [input log] [output log]')
    #     sys.exit(0)

    attendance = AttendanceInfo()
    time.sleep(3)


if __name__ == '__main__':
    main()
