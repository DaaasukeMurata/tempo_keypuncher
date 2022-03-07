#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.edge import service as fs
import os
import sys
import time


def main():
    # selenium起動に失敗するので、http_proxy環境変数無効化
    os.environ['http_proxy'] = ''
    os.environ['https_proxy'] = ''

    edge_service = fs.Service(
        executable_path=resource_path('./webdriver/msedgedriver.exe'))
    driver = webdriver.Edge(service=edge_service)
    driver.get('https://www.yahoo.co.jp/')

    time.sleep(2)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    main()
