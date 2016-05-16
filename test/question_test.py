# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 12:15:28 2016

@author: minxu
"""
import sys
import os
main_dir = os.path.realpath('..')
sys.path.append(main_dir)

import pymongo

try:
    print len(proxies)
except NameError:
    import utils.crawl_proxy as crawl_proxy
    proxies = crawl_proxy.get_proxies()
    
import classes.question as question
import utils.zhihu_login as zhihu_login
from multiprocessing.pool import ThreadPool

def create_question(qid):
    question.crawl_question(qid, session, user_agents, proxies, db)

client = pymongo.MongoClient()
db = client.zhihu
session = zhihu_login.get_session(p_c = 60, p_m = 1000, m_r = 0, p_b = True)
user_agents = zhihu_login.get_agents()
pool = ThreadPool(50)

for u in db.users.find(no_cursor_timeout=True):
    if len(u['questions']) > 0:
        pool.map(create_question, u['questions'])
#    for q in u['questions']:
#        question.crawl_question(q, session, user_agents, proxies, db)
    