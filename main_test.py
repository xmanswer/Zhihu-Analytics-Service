# -*- coding: utf-8 -*-
"""
Created on Tue May 03 10:45:00 2016

@author: Administrator
"""
import pymongo
from Person import Person
import zhihu_login

client = pymongo.MongoClient()
db = client.zhihu
db.users.delete_one({"uid" : "min-xu-26"})
me = Person('min-xu-26', zhihu_login.session, db)
if me.evaluate():
    me.flush_to_db()

followees = me.followees

for u in followees:
    person = Person(u, zhihu_login.session, db)
    if person.evaluate():
        person.flush_to_db()