#!/usr/bin/env python
# coding: utf-8

from logging import getLogger
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WorkTime:
    """1日の勤怠時間"""

    def __init__(self):
        self.date = ''
        self.day_of_week = ''
        self.start_time = ''
        self.end_time = ''


class AttendanceInfo:
    """勤怠情報を取得

    Args:
        webdriver : selenium webdriver
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
            worktime.date = tds[1].text
            worktime.day_of_week = tds[2].text
            worktime.start_time = tds[5].text
            worktime.end_time = tds[6].text

            self.worktimes.append(worktime)

        self.logger.debug('len(worktimes) : %s', len(self.worktimes))
        for wt in self.worktimes:
            self.logger.debug('%s %s %s %s', wt.date,
                              wt.day_of_week, wt.start_time, wt.end_time)
