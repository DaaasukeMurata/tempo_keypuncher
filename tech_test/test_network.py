#!/usr/bin/env python
# coding: utf-8

import urllib.request

url = 'https://www.google.com/'

with urllib.request.urlopen(url) as response:
    print(response.getcode())
