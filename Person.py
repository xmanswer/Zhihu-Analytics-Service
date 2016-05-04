# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 13:02:27 2016

@author: minxu

A Person class for user information crawled from zhihu.com

constructor: specify user_id and login session
features:
multiple fields for user information, multi-threading crawling and data
generation, options for storing data to disk (json) or database (MongoDB)

evaluate: evaluate fields in multi-threading
constructor: 
specify user_id and login session

flush: flush the information of this user to disk
methods:
evaluate(): evaluate fields in multi-threading
flush_to_disk(): flush the information of this user to disk in json format
flush_to_db(): flush the information of this user to MongoDB

fields:
    fields = {
        'uid' : user_id,
        'url' : user_profile_url,
        'agrees' : number_of_agrees,
        'thanks' : number_of_thanks,
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
import Question
import json
import os
import threading

subdir = '/users/'
zhihu_url = "https://www.zhihu.com"
friends_url_dict = {'/followees' : 'ProfileFolloweesListV2', 
                    '/followers' : 'ProfileFollowersListV2'}

TOP = 300

class Person:

    def __init__(self, uid, session):
        self.uid = uid
        self.session = session
        self.url = zhihu_url + '/people/' + uid
        self.personal_soup = BeautifulSoup(session.get(self.url).text)
    
    #evaluate fields in multi-threading
    def evaluate(self):
        connected = False
        while not connected:
            try:
                self.get_friends_num()
                connected = True
            except:
                continue
        threads = []
        
        threads.append(self.methodThread(self.get_agrees()))
        threads.append(self.methodThread(self.get_followers()))
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
            self.connected = False
    
        def run(self):
            while not self.connected:
                try:
                    res = self.method
                    self.connected = True
                except:
                    continue
            return res
    
    #flush the information of this user to disk
    def flush(self):
        self.get_avatar()
        json_dict = {
            'uid' : self.uid,
            'url' : self.url,
            'agrees' : self.agrees,
            'thanks' : self.thanks,
            'followees' : self.followees,
            'followers' :  self.followers,
            'answers' : self.answers,
            'timelines' : self.timelines
        }
        with open(os.getcwd() + subdir + self.uid + '.json', 'w') as f:
            json.dump(json_dict, f, indent=4)
        
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
    
    #wrapper for getting followers
    def get_followers(self):
        self.followers = self.get_friends(self.followers_num, '/followers')
        
    #wrapper for getting followees
    def get_followees(self):
        self.followees = self.get_friends(self.followees_num, '/followees')
        
    #get friends (followers or followees) list of user ids
    def get_friends(self, num, friend_type):
        furl = self.url + friend_type
        fpage = self.session.get(furl).text
        fsoup = BeautifulSoup(fpage)
        flist = []
        for i in xrange((num - 1) / 20 + 1):
            if i == 0: #the first 20 users
                ul = fsoup.find_all("h2", class_="zm-list-content-title")
                for j in xrange(min(num, 20)):
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
                    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                    'Host': "www.zhihu.com",
                    'Referer': furl
                }
                
                r_post = self.session.post(post_url, data=data, headers=header)
                extenedlist = r_post.json()["msg"]
                
                for j in xrange(min(num - i * 20, 20)):
                    soup = BeautifulSoup(extenedlist[j], "lxml")
                    flist.append(soup.find("h2", class_="zm-list-content-title").a['data-tip'][4:])
        
        return flist
    
    #get avatar figure for user
    def get_avatar(self):
        soup = self.personal_soup
        avatar = soup.find("div", class_="zm-profile-header ProfileCard").find( \
        "img", class_="Avatar Avatar--l")["src"]
        r = requests.get(avatar, stream=True)
        with open("figures/img_" + self.uid + ".png", 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
        
    #get all answer texts, return a list of answer texts
    def get_answers(self):
        asoup = BeautifulSoup(self.session.get(self.url + '/answers?page=1').text)
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
            asoup = BeautifulSoup(self.session.get(self.url + '/answers?page=' + str(i)).text)
            for a in asoup.findAll('div', class_="zm-item-rich-text expandable js-collapse-body"):
                answer = self.construct_answer(a)
                answers.append(answer)
                if not Question.check_question(answer['qid']):
                    question = Question.Question(answer['qid'])
                    question.flush()       
                
        self.answers = answers
    
    #get timeline texts up to a certain number (specified by TOP), return a list of them
    def get_timelines(self):
        soup = self.personal_soup
        timelines = []
        total = 0
        
        #construct post method for getting timelines, start_time is the first data_time
        post_url = self.url + "/activities"
        _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
        start_time = soup.find("div", attrs={'class':'zm-profile-section-item zm-item clearfix'})["data-time"]

        data = {
            'start': start_time,
            '_xsrf': _xsrf,
        }
        header = {
            'Host': "www.zhihu.com",
            'Referer': self.url,
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
        }
        
        #accumulate response_size to total, quit crawling timeline texts once
        #no more response or number of docs exceeds threshold value
        r = self.session.post(post_url, data=data, headers=header)
        response_size = r.json()["msg"][0]
        total = total + response_size
        response_html = r.json()["msg"][1]
        for a in BeautifulSoup(response_html).findAll('div', class_="zm-item-rich-text expandable js-collapse-body"):
            answer = self.construct_answer(a)
            timelines.append(answer)
            if not Question.check_question(answer['qid']):
                question = Question.Question(answer['qid'])
                question.flush()   
        
        while total < TOP and response_size > 0:
            data_times = re.findall(r"data-time=\"\d+\"", response_html)
            if len(data_times) > response_size:
                return timelines
            latest_data_time = re.search(r"\d+", data_times[response_size - 1]).group()
            data = {
                'start': latest_data_time,
                '_xsrf': _xsrf,
            }
            r = self.session.post(post_url, data=data, headers=header)
            response_size = r.json()["msg"][0]
            total = total + response_size
            response_html = r.json()["msg"][1]
            for a in BeautifulSoup(response_html).findAll('div', class_="zm-item-rich-text expandable js-collapse-body"):
                answer = self.construct_answer(a)
                timelines.append(answer)
                if not Question.check_question(answer['qid']):
                    question = Question.Question(answer['qid'])
                    question.flush()      
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