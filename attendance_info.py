#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver


def main():
    # argvs = sys.argv
    # if len(argvs) < 2:
    #     print('[usage]python log_will_format.py [input log] [output log]')
    #     sys.exit(0)
    driver = webdriver.Chrome()
    driver.get('https://www.yahoo.co.jp')


if __name__ == '__main__':
    main()
