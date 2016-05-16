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
     abort, render_template, flash, send_file
import thread
#import utils.crawl_proxy as crawl_proxy
SESSION_TYPE = 'mongodb'
USERNAME = 'admin'
PASSWORD = 'default'
SECRET_KEY = 'development key'
LOCAL = False
app = Flask(__name__)
app.config.from_object(__name__)


zhihu_session = zhihu_login.get_session(p_c = 100, p_m = 1000, m_r = 0, p_b = True)
user_agents = zhihu_login.get_agents()
#proxies = crawl_proxy.get_proxies()
client = pymongo.MongoClient()
db = client.zhihu

d = dict()
for glob in db.glob.find():
    d[glob['name']] = glob['value']
d['total_users'] = db.users.count()
d['total_questions'] = db.questions.count()
    
@app.route("/")
def show_msg():    
    return render_template('layout.html', glob = d)

@app.route('/add', methods=['GET'])
def add_person():
    uid = request.args['UID']
    if person.check_person(uid, db):
        u = db.users.find_one({'_id' : uid})
    else:
        thread.start_new_thread(person.crawl_person, (uid, zhihu_session, user_agents,))
        return redirect(url_for('show_msg'))
    
    for i in range(len(u['timelines'])):
        q = db.questions.find_one({'_id' : u['timelines'][i]['qid']})
        u['timelines'][i]['title'] = q['title']
    
    return render_template('show_user.html', user = u)
    
@app.route('/users', methods=['GET'])
def get_top_users():
    users = dict()
    users['users'] = []
    for u in db.users.find():
        users['users'].append(u['uid'])
    
    return render_template('show_users.html', users = users)

@app.route('/get', methods=['GET'])
def get_text():
    uid = request.args['uid']
    user = db.users.find_one({'_id' : uid})
    a = request.args['attri']
    user['attri'] = a
    if a == 'followees':
        user['fns'] = dict()
        for u in user[a]:
            un = db.users.find_one({'_id' : u})
            if un is not None:
                un = un['name']
            else:
                un = u
            user['fns'][u] = un
            
    if a == 'questions':
        user['qs'] = []
        for q in user[a]:
            question = db.questions.find_one({'_id' : q})
            user['qs'].append({'title' : question['title'], 'question' : question['question']})
    
    if a == 'answers' or a == 'timelines':
        for i in range(len(user[a])):
            q = db.questions.find_one({'_id' : user[a][i]['qid']})
            user[a][i]['title'] = q['title']
            
    #return a
    #u = db.users.find_one({'_id' : session.get('uid')})
    return render_template('show_more.html', user = user)
    
@app.route('/figure')
def show_figure():
    uid = request.args.get('uid')
    return send_file(main_dir + '/figures/' + uid + '.png', mimetype = 'image/png')

@app.route('/about')
def show_about():
    return render_template('about.html')

@app.route('/contact')
def show_contact():
    return render_template('contact.html')

if __name__ == "__main__":
    if LOCAL:    
        app.run()
    else:
        app.run(host='0.0.0.0')