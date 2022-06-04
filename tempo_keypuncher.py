#!/usr/bin/env python
# coding: utf-8

import sys
import os
from telnetlib import Telnet
import time
import logging

from selenium import webdriver
from selenium.webdriver.edge import service as fs

from module.attendance_info import AttendanceInfo
from module.operate_tempo import Tempo


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
    # argvs = sys.argv
    # if len(argvs) < 2:
    #     print('[usage]python log_will_format.py [input log] [output log]')
    #     sys.exit(0)FFF

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

    driver = browser()
    attendance = AttendanceInfo(driver)
    tempo = Tempo(driver)

    time.sleep(5)
    driver.quit()


if __name__ == '__main__':
    main()
