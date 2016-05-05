# -*- coding: utf-8 -*-
"""
Created on Tue May 03 10:45:00 2016

@author: Administrator
"""
import pymongo
from Person import Person
import zhihu_login
from multiprocessing.pool import ThreadPool
import thread

def create_user(uid):
    person = Person(uid, session, db)
    if person.evaluate():
        person.flush()

client = pymongo.MongoClient()
db = client.zhihu
#db.users.delete_one({"uid" : "min-xu-26"})
session = zhihu_login.get_session()
me = Person('min-xu-26', session, db)
if me.evaluate():
    me.flush()

me = db.users.find_one({"uid" : "min-xu-26"})

pool = ThreadPool(200)
pool.map(create_user, me['followees'])