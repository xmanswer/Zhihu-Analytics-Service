# -*- coding: utf-8 -*-
"""
Created on Tue May 03 10:45:00 2016

@author: Administrator
"""
import pymongo
from Person import Person
import zhihu_login
from multiprocessing.pool import ThreadPool

def create_user(uid):
    person = Person(uid, zhihu_login.session, db)
    if person.evaluate():
        person.flush()

client = pymongo.MongoClient()
db = client.zhihu
#db.users.delete_one({"uid" : "min-xu-26"})
me = Person('min-xu-26', zhihu_login.session, db)
if me.evaluate():
    me.flush()

followees = me.followees

pool = ThreadPool(10)
pool.map(create_user, followees)