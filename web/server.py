# -*- coding: utf-8 -*-
"""
Created on Thu May 05 12:37:30 2016

@author: minxu
"""
import sys
import os
main_dir = os.path.realpath('..')
sys.path.append(main_dir)
import json
import pymongo
import utils.zhihu_login as zhihu_login
import classes.person as person
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, send_file
import thread
#
#try:
#    print len(proxies)
#except NameError:
#    import utils.crawl_proxy as crawl_proxy
#    proxies = crawl_proxy.get_proxies()

#import utils.crawl_proxy as crawl_proxy
SESSION_TYPE = 'mongodb'
USERNAME = 'admin'
PASSWORD = 'default'
SECRET_KEY = 'development key'
LOCAL = False
NO_KEYWORDS = [{"text" : 'keywords', "size" : 100}, 
    {"text" : 'have', "size" : 50},
    {"text" : 'not', "size" : 60},
    {"text" : 'been', "size" : 70},
    {"text" : 'generated', "size" : 40}]
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
    d['random_users'] = [(u['uid'], u['name'], u['agrees'], u['followers_num']) \
        for u in db.users.aggregate(
            [{'$sample' : {'size' : 10} }]
        )]
    return render_template('layout.html', glob = d)

@app.route('/add', methods=['GET'])
def add_person():
    uid = request.args['UID']
    if person.check_person(uid, db): #search for uid
        u = db.users.find_one({'_id' : uid})
    else: #no uid, search for user name
        u = db.usernames.find_one({'_id' : uid})
        top = dict()
        if u is None: #no user name
            top['attri'] = 'None'
            thread.start_new_thread(person.crawl_person, (uid, zhihu_session, user_agents, proxies, db,))
        else: #return list of users with this user name
            top['attri'] = 'Username'
            top['userlist'] = u['uids']
        return render_template('top_users.html', top = top)
    
    for i in range(len(u['timelines'])):
        q = db.questions.find_one({'_id' : u['timelines'][i]['qid']})
        if q is not None:
            u['timelines'][i]['title'] = q['title']
    
    return render_template('show_user.html', user = u)
    
@app.route('/users', methods=['GET'])
def get_top_users():
    attri = request.args['attri']
    strlist = attri.split('_')
    title = ' '.join(strlist).title()
    top = dict()
    top['attri'] = attri
    top['title'] = title
    top['userlist'] = d[attri]
    top['xdata'] = d['distributions']
    top['xtype'] = strlist[2]
    return render_template('top_users.html', top = top)

@app.route('/contents', methods=['GET'])
def get_top_contents():
    attri = request.args['attri']
    title = ' '.join(attri.split('_')).title()
    top = dict()
    top['attri'] = attri
    top['title'] = title
    top['contentlist'] = d[attri]
    
    return render_template('top_contents.html', top = top)

@app.route('/keywords', methods=['GET'])
def get_top_keywords():
    data = []
    for i in range(len(d['top_keywords'])):
        size = (len(d['top_keywords']) - i) * (len(d['top_keywords']) - i) / (len(d['top_keywords']))
        data.append({"text" : d['top_keywords'][i], "size" : size})
    return render_template('top_keywords.html', data = data)
    
@app.route('/get', methods=['GET'])
def get_text():
    uid = request.args['uid']
    user = db.users.find_one({'_id' : uid})
    a = request.args['attri']
    user['attri'] = a
    if a == 'followees' or a == 'followers':
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
            user['qs'].append({'qid' : q, 'title' : question['title'], 'question' : question['question']})
    
    if a == 'answers' or a == 'timelines':
        for i in range(len(user[a])):
            q = db.questions.find_one({'_id' : user[a][i]['qid']})
            user[a][i]['title'] = q['title']
    
    if a.endswith('keywords'):
        a = '_'.join(a.split())
        data = []
        if a in user:            
            for i in range(len(user[a])):
                size = (len(user[a]) - i) * 100 / (len(user[a]))
                data.append({"text" : user[a][i], "size" : size})
        else:
            for i in range(20):
                data.append(NO_KEYWORDS[i%5])
        user['keywords'] = data

    if a == 'update':
        thread.start_new_thread(person.update_person, (uid, zhihu_session, user_agents, proxies, db,))
    #return a
    #u = db.users.find_one({'_id' : session.get('uid')})
    return render_template('show_more.html', user = user)

@app.route('/question', methods=['GET'])
def get_question():
    qid = request.args.get('qid')
    question = db.questions.find_one({'_id' : qid})
    data = []
    if 'keywords' in question:            
        for i in range(len(question['keywords'])):
            size = (len(question['keywords']) - i) * 100 / (len(question['keywords']))
            data.append({"text" : question['keywords'][i], "size" : size})
    else:
        for i in range(20):
            data.append(NO_KEYWORDS[i%5])
    question['keywords'] = data
    
    return render_template('show_question.html', data = question)

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