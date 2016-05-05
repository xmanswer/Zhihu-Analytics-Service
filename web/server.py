# -*- coding: utf-8 -*-
"""
Created on Thu May 05 12:37:30 2016

@author: minxu
"""
import sys
import os
main_dir = os.path.realpath('..')
sys.path.append(main_dir)

import flask
from flask import Flask, request
import pymongo
import utils.zhihu_login as zhihu_login
import classes.person as person



session = zhihu_login.get_session(p_c = 100, p_m = 1000, m_r = 10, p_b = True)
app = Flask(__name__)
client = pymongo.MongoClient()
db = client.zhihu


@app.route("/")
def hello():
    return "A zhihu.com analytic service"

@app.route("/user", methods = ['GET'])
def get_user():
    uid = request.args.get('uid')
    returnstr = ""
    if person.check_person(uid, db):        
        u = db.users.find_one({"_id" : uid})
    else:
        u = person.crawl_person(uid, session, db)
    returnstr = session.get(u['url']).text
    return returnstr



if __name__ == "__main__":
    app.run()