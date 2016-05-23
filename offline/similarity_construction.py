# -*- coding: utf-8 -*-
"""
Created on Mon May 23 10:40:45 2016

@author: minxu
"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu

def similarity(u, q):
    if len(u) * len(q) == 0:
        return 0
    score = 0
    for w1 in u:
        if w1 in q:
            score += u[w1] * q[w1]
    
    return score