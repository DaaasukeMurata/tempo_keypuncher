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
import logging
# from logging import getLogger, basicConfig, StreamHandler, DEBUG, INFO


class WorkTime:
    """1日の勤怠時間"""

    def __init__(self):
        self.date = ''
        self.day_of_week = ''
        self.start_time = ''
        self.end_time = ''


class AttendanceInfo:
    """勤怠情報を取得"""

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.driver = self._get_driver(browser_type='edge')
        # setting data
        self.SSO_ID = ''        # SSO ID. 設定ファイルから読み込む
        self.SSO_PASS = ''      # SSO Password. 設定ファイルから読み込む
        self.worktimes = []     # WorkTimeを入れる配列。これが勤怠時間

        self._load_setting()    # load settings
        self._login_sso()
        self._get_attendance_info()

        time.sleep(4)

    def __del__(self):
        pass
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
            # "システムに接続されたデバイスが機能していません。 (0x1F)"というerrを表示させない対応
            options = webdriver.EdgeOptions()
            options.add_experimental_option(
                'excludeSwitches', ['enable-logging'])
            options.use_chromium = True
            driver = webdriver.Edge(service=edge_service, options=options)

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

    def _get_attendance_info(self, year=-1, month=-1):
        """勤怠情報の取得

        Args:
            year (int)  : 取得年(ex 2022). 省略可.
            montn (int) : 取得月(ex 3). 省略可
        """
        ATTENDANCE_URL = 'https://cws.local.denso-ten.com/cws/cws?@SID=null&@SUB=root.cws.shuro.personal.aero_personal.aero_personal_menu008&@SN=root.cws.shuro.personal.aero_personal.aero_personal_menu008&@FN=form_aero_menu&@ACTION_LOG_TXT=幹部社員時間外実績照会'
        FORM_YEAR = 'TCDR_NTYEAR'
        FORM_MONTH = 'TCDR_NTMONTH'
        BUTTON_SEARCH = 'doRetrievalButton'

        self.driver.get(ATTENDANCE_URL)

        # input 年月
        # -1(指定なし)の場合は
        if year != -1 and month != -1:
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

        # get attendance table
        # "社員名称"を含むtalbe(tbody)
        elem_td = self.driver.find_element(
            by=By.XPATH, value="//tr/td[text()='社員名称']")
        table = elem_td.find_element(by=By.XPATH, value="../..")
        trs = table.find_elements(by=By.TAG_NAME, value="tr")

        self.logger.debug('len(trs): ${len(trs)}')

        # 先頭は"社員名称 日付 曜日 勤務名称 勤怠区分 出社打刻 退社打刻 管理用時間外"の項目名なので2項目目から取得
        for tr in trs[1:-1]:
            tds = tr.find_elements(by=By.TAG_NAME, value="td")
            worktime = WorkTime()
            # tdsの中身は、"社員名称 日付 曜日 勤務名称 勤怠区分 出社打刻 退社打刻 管理用時間外"の順番
            worktime.date = tds[1].text
            worktime.day_of_week = tds[2].text
            worktime.start_time = tds[5].text
            worktime.end_time = tds[6].text

            self.worktimes.append(worktime)

        self.logger.debug('len(worktimes) : %s', len(self.worktimes))
        for wt in self.worktimes:
            self.logger.debug('%s %s %s %s', wt.date,
                              wt.day_of_week, wt.start_time, wt.end_time)


def main():
    # argvs = sys.argv
    # if len(argvs) < 2:
    #     print('[usage]python log_will_format.py [input log] [output log]')
    #     sys.exit(0)FFF

    ################
    # for LOGGER -> 
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create console handler with a INFO log level
    ch = logging.StreamHandler()
    # ch.setLevel(logging.INFO)
    ch.setLevel(logging.DEBUG)
    # ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
    ch_formatter = logging.Formatter(
        '%(filename)s - %(funcName)s : %(message)s')
    ch.setFormatter(ch_formatter)

    # add the handlers to the logger
    # logger.addHandler(fh)
    logger.addHandler(ch)
    # <- for LOGGER
    ################

    attendance = AttendanceInfo()
    time.sleep(3)


if __name__ == '__main__':
    main()
