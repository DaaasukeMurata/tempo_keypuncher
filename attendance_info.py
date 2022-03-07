#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import os


def main():
    # argvs = sys.argv
    # if len(argvs) < 2:
    #     print('[usage]python log_will_format.py [input log] [output log]')
    #     sys.exit(0)

    browser = init()
    browser.get('https://www.yahoo.co.jp')



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


if __name__ == '__main__':
    main()
