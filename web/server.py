# -*- coding: utf-8 -*-
"""
Created on Thu May 05 12:37:30 2016

@author: minxu
"""
import sys
import os
main_dir = os.path.realpath('..')
sys.path.append(main_dir)

import pymongo
import utils.zhihu_login as zhihu_login
import classes.person as person
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
#import utils.crawl_proxy as crawl_proxy
     
SESSION_TYPE = 'mongodb'
USERNAME = 'admin'
PASSWORD = 'default'
SECRET_KEY = 'development key'
app = Flask(__name__)
app.config.from_object(__name__)


zhihu_session = zhihu_login.get_session(p_c = 100, p_m = 1000, m_r = 0, p_b = True)
user_agents = zhihu_login.get_agents()
#proxies = crawl_proxy.get_proxies()
client = pymongo.MongoClient()
db = client.zhihu


@app.route("/")
def show_msg():    
    return render_template('layout.html')

@app.route('/add', methods=['POST'])
def add_person():
    uid = request.form['uid']
    if person.check_person(uid, db):
        flash('User exists')
        u = db.users.find_one({'_id' : uid})
    else:
        flash('User does not exist, crawling profile' + '.' * 10)
        u = person.crawl_person(uid, zhihu_session, user_agents)
    return render_template('show_user.html', user = u)

@app.route('/users', methods=['GET'])
def get_users():
    users = dict()
    users['users'] = []
    for u in db.users.find():
        users['users'].append(u['uid'])
    return render_template('show_users.html', users = users)

@app.route('/get', methods=['GET'])
def get_text():
    a = request.args['attri']
    uid = request.args['uid']
    data = dict()
    data['attri'] = a
    user = db.users.find_one({'_id' : uid})
    data['dat'] = user[a]
    if a == 'questions':
        data['questions'] = []
        for q in user[a]:
            question = db.questions.find_one({'_id' : q})
            data['questions'].append({'title' : question['title'], 'question' : question['question']})
    #return a
    #u = db.users.find_one({'_id' : session.get('uid')})
    return render_template('show_more.html', data = data)
    

if __name__ == "__main__":
    app.run()