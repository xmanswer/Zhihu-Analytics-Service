# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 13:02:27 2016

@author: minxu

A Person class for user information crawled from zhihu.com

constructor: specify user_id and login session, db is optional for database 
storage type, default is None (file storage type)

features:
multiple fields for user information, multi-threading crawling and data
generation, options for storing data to disk (json) or database (MongoDB)

constructor: 
specify user_id and login session

methods:
evaluate(): evaluate fields in multi-threading
flush(): flush all information for this user to file/database depending on 
the storage mode

fields:
    fields = {
        'uid' : user_id,
        'url' : user_profile_url,
        'name' : user_zhihu_name,
        'agrees' : number_of_agrees,
        'thanks' : number_of_thanks,
        'followers_num': self.followers_num,
        'followees_num' : self.followees_num,
        'followees' : [list_of_followees],
        'followers' :  [list_of_followers],
        'answers' : [list_of_dicts_for_user_answers {
                        'url' : answer_url,
                        'text' : answer_text,
                        'qid' : question_id,
                        'aid' : answer_id,
        
        }],
        'timelines' : [list_of_dicts_for_timeline_answers {
                        'url' : answer_url,
                        'text' : answer_text,
                        'qid' : question_id,
                        'aid' : answer_id,
        
        }],
        'questions' : set_of_question_ids 
    }
"""

from bs4 import BeautifulSoup
import re
import requests
import json
import os
import threading
import pymongo
import time
import random
import question

__DEBUG__ = False
__LOG__ = False

main_dir = os.path.realpath('..')

import analysis.keyword_extraction as keyword_extraction

LOG = main_dir + '/logs/'
subdir = '/users/'
zhihu_url = "https://www.zhihu.com"
friends_url_dict = {'/followees' : 'ProfileFolloweesListV2', 
                    '/followers' : 'ProfileFollowersListV2'}
#user_agent = 'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0'
user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0"
TOP = 100
TIMEOUT = 20
SLEEPTIME = 0.01

class Person:

    def __init__(self, uid, session, user_agents = [user_agent], proxies = None, db = None):
        self.uid = uid
        self.session = session
        self.url = zhihu_url + '/people/' + uid
        self.db = db
        self.user_agents = user_agents
        self.proxies = proxies
        if __LOG__:
            self.log = open(LOG + uid + '.log', 'w')
    
    #evaluate fields in multi-threading
    def evaluate(self):
        self.personal_soup = BeautifulSoup(self.reliable_get(self.url))
        self.get_friends_num()
        self.questions = set()
        
        threads = []
        
        threads.append(self.methodThread(self.get_agrees()))
        threads.append(self.methodThread(self.get_name()))
        #threads.append(self.methodThread(self.get_followers()))
        threads.append(self.methodThread(self.get_followees()))
        threads.append(self.methodThread(self.get_answers()))
        threads.append(self.methodThread(self.get_timelines()))
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
    #child class for multi-thread evaluating different fields        
    class methodThread (threading.Thread):
        def __init__(self, method):
            threading.Thread.__init__(self)
            self.method = method
    
        def run(self):
            return self.method
    
    #wrapper for flush all information for this question to file/database 
    #depending on the storage mode 
    def flush(self):
        if self.db is None:
            self.flush_to_file()
        else:
            self.flush_to_db()
        if __LOG__:
            self.log.close()
        
    #flush data to database
    def flush_to_db(self):
        self.get_avatar()
        try:
            self.db.users.insert_one(self.construct_data())        
        except pymongo.errors.DuplicateKeyError:
            self.db.users.delete_one({'_id' : self.uid})
            self.db.users.insert_one(self.construct_data())
    
    #flush data to file in json format
    def flush_to_file(self):
        self.get_avatar()
        json_dict = self.construct_data()
        with open(main_dir + subdir + self.uid + '.json', 'w') as f:
            json.dump(json_dict, f, indent=4)
    
    #flush the information of this user to disk
    def construct_data(self):
        data = {
            '_id' : self.uid, #for MongoDB
            'uid' : self.uid,
            'url' : self.url,
            'name' : self.name,
            'agrees' : self.agrees,
            'thanks' : self.thanks,
            'followers_num': self.followers_num,
            'followees_num' : self.followees_num,
            'followees' : self.followees,
            #'followers' :  self.followers,
            'answers' : self.answers,
            'timelines' : self.timelines,
            'questions' : list(self.questions)
        }
        return data
        
    #get total number of followees and followers
    def get_friends_num(self):
        soup = self.personal_soup
        alla = soup.find("div", class_="zm-profile-side-following zg-clear").findAll("a")
        self.followees_num, self.followers_num = int(alla[0].strong.string), int(alla[1].strong.string)
    
    #get total number of agrees and thanks received
    def get_agrees(self):
        soup = self.personal_soup
        self.agrees = int(soup.find("span", class_="zm-profile-header-user-agree").strong.string)
        self.thanks = int(soup.find("span", class_="zm-profile-header-user-thanks").strong.string)
    
    def get_name(self):    
        soup = self.personal_soup
        self.name = soup.find('div', class_="title-section ellipsis").find('span', class_="name").string
        
    #wrapper for getting followers
    def get_followers(self):
        self.followers = self.get_friends(self.followers_num, '/followers')
        
    #wrapper for getting followees
    def get_followees(self):
        self.followees = self.get_friends(self.followees_num, '/followees')
    
    #get friends (followers or followees) list of user ids
    def get_friends(self, num, friend_type):
        furl = self.url + friend_type
        fpage = self.reliable_get(furl)
        fsoup = BeautifulSoup(fpage)
        flist = []
        for i in xrange((num - 1) / 20 + 1):
            if i == 0: #the first 20 users
                ul = fsoup.find_all("h2", class_="zm-list-content-title")
                for j in xrange(min(num, len(ul))):
                    flist.append(ul[j].a['data-tip'][4:])
            else: #more users, need to specify offsets to post request
                post_url = "http://www.zhihu.com/node/" + friends_url_dict[friend_type]
                _xsrf = fsoup.find("input", attrs={'name': '_xsrf'})["value"]
                offset = i * 20
                
                hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", fpage)[0]
                
                params = json.dumps({"offset": offset, "order_by": "created", "hash_id": hash_id})
                data = {
                    '_xsrf': _xsrf,
                    'method': "next",
                    'params': params
                }
                header = {
                    #'User-Agent': ,
                    'User-Agent' : random.choice(self.user_agents),
                    'Host': "www.zhihu.com",
                    'Referer': furl
                }
                
                extenedlist = self.reliable_post(post_url, data, header)
                
                for j in xrange(0, len(extenedlist)):
                    soup = BeautifulSoup(extenedlist[j], "lxml")
                    flist.append(soup.find("h2", class_="zm-list-content-title").a['data-tip'][4:])
        
        return flist
    
    #get avatar figure for user
    def get_avatar(self):
        soup = self.personal_soup
        avatar = soup.find("div", class_="zm-profile-header ProfileCard").find( \
        "img", class_="Avatar Avatar--l")["src"]
        connected = False
        while not connected:
            try:
                r = requests.get(avatar, stream=True, timeout = TIMEOUT, proxies = {
                                'https': random.choice(self.proxies)                    
                            })
                with open(main_dir + "/figures/" + self.uid + ".png", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                connected = True
            except Exception as e:
                if __DEBUG__:
                    print self.uid, e
                if __LOG__:
                    self.log.write(str(e) + '\n')
        
    #get all answer texts, return a list of answer texts
    def get_answers(self):
        asoup = BeautifulSoup(self.reliable_get(self.url + '/answers?page=1'))
        pagesection = asoup.find("div",  class_="zm-invite-pager")
        pagesize = 0
        answers = []
        
        #get number of pages first
        if pagesection == None:
            pagesize = 1
        else:
            spanall = pagesection.findAll("span")
            for span in spanall:
                if span.a != None and span.a.string.isdigit():
                    pagesize = max(pagesize, int(span.a.string))
        
        #get answer texts for each page
        for i in range(1, pagesize + 1):
            if len(answers) > TOP: 
                break
            asoup = BeautifulSoup(self.reliable_get(self.url + '/answers?page=' + str(i)))
            for a in asoup.findAll('div', class_="zm-item-rich-text expandable js-collapse-body"):
                answer = self.construct_answer(a)
                answers.append(answer)
                self.questions.add(answer['qid']) 
                
        self.answers = answers
    
    #get timeline texts up to a certain number (specified by TOP), return a list of them
    def get_timelines(self):
        soup = self.personal_soup
        timelines = []
        total = 0
        
        #construct post method for getting timelines, start_time is the first data_time
        post_url = self.url + "/activities"
        _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
        sts = soup.find("div", attrs={'class':'zm-profile-section-item zm-item clearfix'})
        if sts is not None:
            start_time = sts["data-time"]
        else:
            self.timelines = timelines
            return

        data = {
            'start': start_time,
            '_xsrf': _xsrf,
        }
        header = {
            'Host': "www.zhihu.com",
            'Referer': self.url,
            'User-Agent': random.choice(self.user_agents),
        }
        
        #accumulate response_size to total, quit crawling timeline texts once
        #no more response or number of docs exceeds threshold value
        r_msg = self.reliable_post(post_url, data, header)
        response_size = r_msg[0]
        total = total + response_size
        response_html = r_msg[1]
        for a in BeautifulSoup(response_html).findAll('div', class_="zm-item-rich-text expandable js-collapse-body"):
            answer = self.construct_answer(a)
            timelines.append(answer)
            self.questions.add(answer['qid']) 
        
        while total < TOP and response_size > 0:
            data_times = re.findall(r"data-time=\"\d+\"", response_html)
            if len(data_times) > response_size:
                return timelines
            latest_data_time = re.search(r"\d+", data_times[response_size - 1]).group()
            data = {
                'start': latest_data_time,
                '_xsrf': _xsrf,
            }
            r_msg = self.reliable_post(post_url, data, header)
            response_size = r_msg[0]
            total = total + response_size
            response_html = r_msg[1]
            for a in BeautifulSoup(response_html).findAll('div', class_="zm-item-rich-text expandable js-collapse-body"):
                answer = self.construct_answer(a)
                timelines.append(answer)
                self.questions.add(answer['qid'])
                
        self.timelines = timelines
    
    #help method for constructing an answer structure
    def construct_answer(self, a):
        a_text = re.sub('<[^>]+>', '', a.find('textarea', class_="content").string) #filter <garbage>
        a_url = a["data-entry-url"]
        a_url_arr = a_url.split('/')
        answer = {
            'url' : a_url,
            'text' : a_text,
            'qid' : a_url_arr[2],
            'aid' : a_url_arr[4],
        }
        return answer
    
    #a reliable get method, will keep trying is fail, change proxy everytime
    def reliable_get(self, url):
        connected = False
        while not connected:
            try:
                self.session.headers['User-Agent'] = random.choice(self.user_agents)
                r = self.session.get(url, timeout = TIMEOUT, proxies = {
                        'https': random.choice(self.proxies)
                    }).text
                time.sleep(SLEEPTIME)
                connected = True
            except Exception as e: 
                if __DEBUG__:
                    print self.uid, url, e
                if __LOG__:
                    self.log.write(url + ' ' + str(e) + '\n')
        return r
    
    #a reliable post method, will keep trying is fail, change proxy everytime
    def reliable_post(self, url, data, header):
        connected = False
        while not connected:
            try:
                r = self.session.post(url, data=data, headers=header, \
                    timeout = TIMEOUT, proxies = {
                        'https': random.choice(self.proxies)                    
                    })
                time.sleep(SLEEPTIME)
                r_msg = r.json()["msg"]
                connected = True                
            except Exception as e: 
                if __DEBUG__:
                    print self.uid, url, e
                if __LOG__:
                    self.log.write(url + ' ' + str(e) + '\n')
        return r_msg        
        
#check if this question object exists in database or file
def check_person(uid, db = None):
    if db is None:
        return os.path.exists(main_dir + subdir + uid + '.json')
    else:
        return db.users.find({'_id' : uid}).count() != 0

#crawl the Person with given uid to disk, return the dictionary for this person
def crawl_person(uid, session, user_agents = [user_agent], proxies = None, db = None):
    if not check_person(uid, db):
        print 'creating user ' + uid
        p = Person(uid, session, user_agents, proxies, db)
        p.evaluate()
        p.flush()
        print 'created user ' + uid
        
    if db is not None:
        return db.users.find_one({"_id" : uid})
    else:
        with open(main_dir + subdir + uid + '.json') as f: 
            return json.load(f)

#crawl the Person with given uid to disk, return the dictionary for this person
def update_person(uid, session, user_agents = [user_agent], proxies = None, db = None):
    print 'updating user ' + uid
    p = Person(uid, session, user_agents, proxies, db)
    p.evaluate()
    for qid in p.questions:
        question.crawl_question(qid, session, user_agents, proxies, db)
    p.flush()
    keyword_extraction.generate_user_keywords(uid, db)
    for qid in p.questions:
        keyword_extraction.generate_question_keywords(qid, db)
        
    print 'updated user ' + uid
        
    if db is not None:
        return db.users.find_one({"_id" : uid})
    else:
        with open(main_dir + subdir + uid + '.json') as f: 
            return json.load(f)