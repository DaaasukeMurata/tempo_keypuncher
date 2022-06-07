#!/usr/bin/env python
# coding: utf-8
from pickle import TRUE
import time
import sys
import os
import json
import logging
from logging import getLogger
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.edge import service as fs
import requests
import datetime


class Tempo:
    """ Tempo Operator

    Args:
        webdriver : selenium webdriver
    """

    LOGIN_URL = 'https://jira.geniie.net/login.jsp?permissionViolation=true&os_destination=%2Fsecure%2FTempo.jspa&page_caps=&user_role=#/my-work/week?type=LIST'
    ADD_URL = 'https://jira.geniie.net/rest/tempo-timesheets/4/worklogs/'
    DELETE_URL = 'https://jira.geniie.net/rest/tempo-timesheets/4/worklogs/'
    SEARCH_URL = 'https://jira.geniie.net/rest/tempo-timesheets/3/worklogs?'

    def __init__(self, webdriver):
        self.logger = getLogger('tempo_keypuncher')
        self.driver = webdriver
        self.session = None
        self.jirauser = ''
        self._load_stting()
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

        # requests libのsessionにcookie情報受け渡し
        self.session = requests.session()
        for cookie in self.driver.get_cookies():
            self.logger.debug('cookie : %s', cookie)
            self.session.cookies.set(cookie['name'], cookie['value'])
        self.logger.debug('session.cookies : %s', self.session.cookies)

    def _load_stting(self):
        with open('./setting.json') as setting_file:
            settings = json.load(setting_file)
            self.jirauser = settings['TEMPO_JIRAUSER']

    def add(self, origin_taskid, date, spent_hour, is_primary_work=TRUE):
        """ Tempoに業務追加

        Args:
            origin_taskid (int) : Tempoのjira projectNo (ex. 57880)
            date (datatime.date()) : 作業日 (ex. datatime.date(2022, 6, 1))
            spent_hour (int) : 作業時間. 時間単位
            is_primary_work (bool) : Tempoの"正味" / "非正味". TRUE->正味、FALSE->非正味

        Returns:
            なし
        """
        # TempoServerにPostするデータ作成
        syomi = '非正味'
        if is_primary_work:
            syomi = '正味'
        payload = {
            "attributes": {
                "_正味／非正味_": {
                    "name": "正味/非正味",
                    "workAttributeId": 6,
                    "value": syomi
                }
            },
            "worker": self.jirauser,
            "started": date.strftime('%Y-%m-%d'),
            "timeSpentSeconds": int(spent_hour * 3600),
            "originTaskId": str(origin_taskid),
        }
        self.logger.debug('json.dumps(payload): %s', json.dumps(payload))
        headers = {'content-type': 'application/json'}

        # Post to server
        res = self.session.post(
            self.ADD_URL, data=json.dumps(payload), headers=headers)
        self.logger.debug('result_post : %s', res)
        self.logger.debug('result_post.headers : %s', res.headers)

        # TODO error処理

    def delete(self, worklog_id):
        """ 指定されたWorklogの削除

        Args:
            worklog_id (int): 削除するworklog id

        Returns:
            なし
        """
        # 以下の形式でDELETE
        # https://jira.geniie.net/rest/tempo-timesheets/4/worklogs/898521
        url = self.DELETE_URL + str(worklog_id)
        self.logger.debug('url:%s', url)
        res = self.session.delete(url)
        self.logger.debug('delete_res: %s', res)

    def search_worklogs(self, start_date, end_date):
        """ 特定期間のworklog ID取得

        Args:
            start_date (datatime.date) : 開始日
            end_date   (datatime.date) : 終了日

        Returns:
            int[] : ヒットしたWorklog ID
        """
        # 以下の形式でGET
        # https://jira.geniie.net/rest/tempo-timesheets/3/worklogs?dateFrom=2022-05-21&dateTo=2022-06-20
        url = self.SEARCH_URL + 'dateFrom=' + \
            start_date.strftime('%Y-%m-%d') + '&dateTo=' + \
            end_date.strftime('%Y-%m-%d')
        self.logger.debug('Search GET url: %s', url)
        res = self.session.get(url)
        # TODO error処理
        res_data = res.json()
        self.logger.info('hit count: %s', len(res_data))
        # self.logger.debug('res_data: %s', json.dumps(res_data, indent=4))

        # worklog IDの取得
        worklog_ids = []
        for data in res_data:
            worklog_ids.append(data['id'])  # 'id'に、worklog IDが入っている
        self.logger.info('ids: %s', worklog_ids)
        return worklog_ids


def main():
    _logger_init()

    driver = _browser()
    tempo = Tempo(driver)
    # tempo.add(57880, datetime.date(2022, 6, 2),
    #           spent_hour=2.5, is_primary_work=TRUE)
    ids = tempo.search_worklogs(datetime.date(2022, 5, 21),
                                datetime.date(2022, 6, 20))
    tempo.delete(ids[0])
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
