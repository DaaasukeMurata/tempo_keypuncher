#!/usr/bin/env python
# coding: utf-8
import time
import sys
import os
import json
from logging import getLogger
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.edge import service as fs


class Tempo:
    """ Tempo Operator

    Args:
        webdriver : selenium webdriver
    """

    LOGIN_URL = 'https://jira.geniie.net/login.jsp?permissionViolation=true&os_destination=%2Fsecure%2FTempo.jspa&page_caps=&user_role=#/my-work/week?type=LIST'

    def __init__(self, webdriver):
        self.logger = getLogger('tempo_keypuncher')
        self.driver = webdriver
        self._login()

    def _login(self):
        """ login tempo
        """
        FORM_ID = 'login-form-username'
        FORM_PASS = 'login-form-password'
        BUTTON_LOGIN = 'login-form-submit'

        # load setting
        with open('./setting.json') as setting_file:
            settings = json.load(setting_file)
            geniie_id = settings['GENIIE_ID']
            geniie_pass = settings['GENIIE_PASS']

        self.driver.get(self.LOGIN_URL)

        # input login_id / password
        id = self.driver.find_element(by=By.ID, value=FORM_ID)
        id.send_keys(geniie_id)
        password = self.driver.find_element(by=By.ID, value=FORM_PASS)
        password.send_keys(geniie_pass)
        btn_login = self.driver.find_element(by=By.ID, value=BUTTON_LOGIN)
        btn_login.click()


def browser(browser_type='edge'):
    """browser_typeに応じたwebdriverの取得 

    Args:
        browser_type (str): 'edge' or 'chrome'

    Return:
        webdriver : webdriver for edge or chrome
    """
    # OSの環境変数に、http_proxy, https_proxyがあるとselenium起動に失敗するため無効化
    # I guesss selenium fails to access localhost(127,0,0,*).
    os.environ['http_proxy'] = ''
    os.environ['https_proxy'] = ''

    # browser_typeに応じたdriverの取得
    driver = None
    wk_browser = browser_type.lower()
    if wk_browser == 'edge':
        edge_service = fs.Service(executable_path='./msedgedriver.exe')
        # "システムに接続されたデバイスが機能していません。 (0x1F)"というerrを表示させない対応
        options = webdriver.EdgeOptions()
        options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        options.use_chromium = True
        driver = webdriver.Edge(service=edge_service, options=options)

    elif wk_browser == 'chrome':
        driver = webdriver.Chrome()
    else:
        print('ERROR: browser_type : "%s" is invalid.' %
              (browser_type), file=sys.stderr)
        sys.exit(1)
    return driver


def main():
    driver = browser()
    Tempo(driver)
    driver.quit()

    time.sleep(3)


if __name__ == '__main__':
    main()
