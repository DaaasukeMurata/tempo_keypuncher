#!/usr/bin/env python
# coding: utf-8

from logging import getLogger
import logging
import os
import sys
import json
from time import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.edge import service as fs
import datetime


class WorkTime:
    """1日の勤怠時間

    Member:
        date (datatime.date)       : 日付
        start_time (datatime.time) : 開始時刻
        end_time   (datatime.time) : 終了時刻
        spent_time (datatime.timedelta) : 業務時間
    """

    def __init__(self):
        self.logger = getLogger('tempo_keypuncher')
        self._date = None
        self._start_time = None
        self._end_time = None

    @property
    def date(self):
        """ date (datatime.date) : 日付 """
        return self._date

    @date.setter
    def date(self, val):
        if type(val) is str:
            # '2022/05/24' の形式
            # self._date = datetime.datetime.strptime(val, '%Y/%m/%d').date
            self._date = datetime.datetime.strptime(val, '%Y/%m/%d')
            self._date = self._date.date()

        elif type(val) is datetime.date:
            self._date = val
        else:
            self.logger.error('setter with illigal val: %s', val)

    @property
    def start_time(self):
        """ start_time (datatime.time) : 開始時刻 """
        return self._start_time

    @start_time.setter
    def start_time(self, val):
        if type(val) is str:
            self._start_time = self._str2time(val)
        elif type(val) is datetime.time:
            self._start_time = val
        else:
            self.logger.error('setter with illigal val: %s', val)

    @property
    def end_time(self):
        """ end_time (datatime.time) : 終了時刻 """
        return self._end_time

    @end_time.setter
    def end_time(self, val):
        if type(val) is str:
            self._end_time = self._str2time(val)
        elif type(val) is datetime.time:
            self._end_time = val
        else:
            self.logger.error('setter with illigal val: %s', val)

    @property
    def spent_time(self):
        """ spent_time (datatime.timedelta) : 業務時間　"""
        if self._start_time is None or self._end_time is None:
            return None
        start = datetime.datetime.combine(
            datetime.date.today(), self._start_time)
        end = datetime.datetime.combine(
            datetime.date.today(), self._end_time)
        return end - start

    def _str2time(self, str_val):
        # '08:19'の形式
        try:
            wk = datetime.datetime.strptime(str_val, '%H:%M')
            wk = wk.time()
        except ValueError as e:
            wk = None
        return wk


class AttendanceInfo:
    """勤怠情報を取得

    Args:
        webdriver (selenium.webdriver) : selenium webdriver
    """

    LOGIN_URL = 'https://cws.local.denso-ten.com/cws/cws'
    ATTENDANCE_URL = 'https://cws.local.denso-ten.com/cws/cws?@SID=null&@SUB=root.cws.shuro.personal.aero_personal.aero_personal_menu008&@SN=root.cws.shuro.personal.aero_personal.aero_personal_menu008&@FN=form_aero_menu&@ACTION_LOG_TXT=幹部社員時間外実績照会'

    def __init__(self, webdriver):
        self.logger = getLogger('tempo_keypuncher')

        self.driver = webdriver
        self.worktimes = []     # WorkTimeを入れる配列。これが勤怠時間

        self._login_sso()
        self._get_attendance_info()

    def __del__(self):
        pass

    def worktime(self, date):
        """ 指定された日時のWorkTimeを取得
            指定された日時が存在しない場合、Noneを返却

            Args:
                date (datetime.date): 日付
            Returns:
                WorkTime: 勤怠時間。
        """
        for wk in self.worktimes:
            if wk.date == date:
                return wk
        return None

    def _load_setting(self):
        """load settings from ""./setting.json
        """
        with open('./setting.json') as setting_file:
            settings = json.load(setting_file)
            return settings['SSO_ID'], settings['SSO_PASS']

    def _login_sso(self):
        """ login SSO
        """
        FORM_ID = 'username'
        FORM_PASS = 'uid_password'
        BUTTON_LOGIN = 'uid_submit'

        sso_id, sso_pass = self._load_setting()    # load settings
        self.driver.get(self.LOGIN_URL)

        # input SSO ID/PASS
        id = self.driver.find_element(by=By.ID, value=FORM_ID)
        id.send_keys(sso_id)
        password = self.driver.find_element(by=By.ID, value=FORM_PASS)
        password.send_keys(sso_pass)
        btn_login = self.driver.find_element(by=By.ID, value=BUTTON_LOGIN)
        btn_login.click()

    def _get_attendance_info(self, year=-1, month=-1):
        """勤怠情報の取得

        Args:
            year (int)  : 取得年(ex 2022). 省略可.
            montn (int) : 取得月(ex 3). 省略可
        """
        FORM_YEAR = 'TCDR_NTYEAR'
        FORM_MONTH = 'TCDR_NTMONTH'
        BUTTON_SEARCH = 'doRetrievalButton'

        self.driver.get(self.ATTENDANCE_URL)

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

        # 先頭は"社員名称 日付 曜日 勤務名称 勤怠区分 出社打刻 退社打刻 管理用時間外"の項目名なので2項目目から取得
        for tr in trs[1:-1]:
            tds = tr.find_elements(by=By.TAG_NAME, value="td")
            worktime = WorkTime()
            # tdsの中身は、"社員名称 日付 曜日 勤務名称 勤怠区分 出社打刻 退社打刻 管理用時間外"の順番
            self.logger.debug('tds0: %s 1: %s 2: %s 3: %s 4: %s 5: %s 6: %s',
                              tds[0].text, tds[1].text, tds[2].text, tds[3].text, tds[4].text, tds[5].text, tds[6].text)
            worktime.date = tds[1].text
            worktime.start_time = tds[5].text
            worktime.end_time = tds[6].text
            self.worktimes.append(worktime)

        self.logger.debug('len(worktimes) : %s', len(self.worktimes))
        for wt in self.worktimes:
            self.logger.debug('%s start: %s end: %s', wt.date,
                              wt.start_time, wt.end_time)


def main():
    # argvs = sys.argv
    # if len(argvs) < 2:
    #     print('[usage]python log_will_format.py [input log] [output log]')
    #     sys.exit(0)FFF

    _logger_init()

    driver = _browser()
    attendance = AttendanceInfo(driver)
    wktime = attendance.worktime(datetime.date(2022, 6, 1))
    print(wktime.date)
    print(wktime.start_time)
    print(wktime.end_time)
    print(wktime.spent_time)
    driver.quit()


def _logger_init():
    # for LOGGER ----------->
    logger = logging.getLogger('tempo_keypuncher')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()  # for console
    # ch.setLevel(logging.INFO)
    ch.setLevel(logging.DEBUG)
    ch_formatter = logging.Formatter(
        '%(filename)s - %(funcName)s : %(message)s')
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)
    # <----------- for LOGGER


def _browser(browser_type='edge'):
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

    driver.set_window_size(100, 200)
    return driver


if __name__ == '__main__':
    main()
