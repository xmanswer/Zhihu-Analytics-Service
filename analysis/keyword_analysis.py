# -*- coding: utf-8 -*-
"""
Created on Thu May 12 09:48:01 2016

@author: minxu
"""
import sys
import os
main_dir = os.path.realpath('..')
sys.path.append(main_dir)

import analysis.keyword_extraction as keyword_extraction

import pymongo
import thread
from multiprocessing.pool import ThreadPool


client = pymongo.MongoClient()
db = client.zhihu

pool1 = ThreadPool(80)
pool2 = ThreadPool(80)


thread.start_new_thread(keyword_extraction.generate_users_keywords, (db, pool1,))
thread.start_new_thread(keyword_extraction.generate_questions_keywords, (db, pool2,))
