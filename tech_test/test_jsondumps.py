#!/usr/bin/env python
# coding: utf-8

import json

dict = {'dataname1': 'data1', 'dataname2': 777}

json_data = json.dumps(dict)

print(json_data)
