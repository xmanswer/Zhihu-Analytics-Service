# -*- coding: utf-8 -*-
"""
Created on Wed May 18 15:14:06 2016

@author: minxu
"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu
visited = set()

