# -*- coding: utf-8 -*-
"""
Created on Tue May 03 10:45:00 2016

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
    
import classes.person as person
import utils.zhihu_login as zhihu_login
from multiprocessing.pool import ThreadPool

def create_user(uid):
    person.crawl_person(uid, session, user_agents, proxies, db)

client = pymongo.MongoClient()
db = client.zhihu
session = zhihu_login.get_session(p_c = 20, p_m = 2000, m_r = 0, p_b = True)
user_agents = zhihu_login.get_agents()

me = person.crawl_person("min-xu-26", session, user_agents, proxies, db)

#pool = ThreadPool(20)
#pool.map(create_user, me['followees'])
for u in me['followees']:
    create_user(u)