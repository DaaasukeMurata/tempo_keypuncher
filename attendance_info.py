#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge import service as fs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary  # need to run 'pip install chromedriver-binary-auto'
import sys
import os
import time
import json


class AttendanceInfo:
    """勤怠情報を取得"""

    def __init__(self):
        self.driver = self._get_driver(browser_type='edge')
        # setting data
        self.SSO_ID = ''
        self.SSO_PASS = ''
        self._load_setting()    # load settings

        self._login_sso()
        self._get_attendace_info(year=2022, month=2)

    def __del__(self):
        self.driver.quit()

    def _load_setting(self):
        """load settings from ""./setting.json
        """
        with open('./setting.json') as setting_file:
            settings = json.load(setting_file)
            self.SSO_ID = settings['SSO_ID']
            self.SSO_PASS = settings['SSO_PASS']

    def _get_driver(self, browser_type='edge'):
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
        browser = browser_type.lower()
        if browser == 'edge':
            edge_service = fs.Service(executable_path='./msedgedriver.exe')
            driver = webdriver.Edge(service=edge_service)
        elif browser == 'chrome':
            driver = webdriver.Chrome()
        else:
            print('ERROR: browser_type : "%s" is invalid.' %
                  (browser_type), file=sys.stderr)
            sys.exit(1)
        return driver

    def _login_sso(self):
        """SSO へログイン
        """
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
        btn_login = self.driver.find_element(by=By.ID, value=BUTTON_LOGIN)
        btn_login.click()

    def _get_attendace_info(self, year=2022, month=3):
        """勤怠情報の取得

        Args:
            year (int)  : 取得年(ex 2022)
            montn (int) : 取得月(ex 3)
        """
        ATTENDANCE_URL = 'https://cws.local.denso-ten.com/cws/cws?@SID=null&@SUB=root.cws.shuro.personal.aero_personal.aero_personal_menu008&@SN=root.cws.shuro.personal.aero_personal.aero_personal_menu008&@FN=form_aero_menu&@ACTION_LOG_TXT=幹部社員時間外実績照会'
        FORM_YEAR = 'TCDR_NTYEAR'
        FORM_MONTH = 'TCDR_NTMONTH'
        BUTTON_SEARCH = 'doRetrievalButton'

        self.driver.get(ATTENDANCE_URL)

        # input 年月
        form_year = self.driver.find_element(by=By.ID, value=FORM_YEAR)
        form_year.send_keys(year)
        form_month = self.driver.find_element(by=By.ID, value=FORM_MONTH)
        form_month.send_keys(month)
        btn_search = self.driver.find_element(by=By.ID, value=BUTTON_SEARCH)
        btn_search.click()

        # wait until someid is clickable
        wait = WebDriverWait(self.driver, 20)
        element = wait.until(
            EC.element_to_be_clickable((By.ID, BUTTON_SEARCH)))

        print('xxxxxxxxxxxxxxxx 検索ボタン clickable')

        time.sleep(10)


def main():
    # argvs = sys.argv
    # if len(argvs) < 2:
    #     print('[usage]python log_will_format.py [input log] [output log]')
    #     sys.exit(0)

    attendance = AttendanceInfo()
    time.sleep(3)


if __name__ == '__main__':
    main()
