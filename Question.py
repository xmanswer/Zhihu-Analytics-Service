# -*- coding: utf-8 -*-
"""
Created on Mon May 02 16:04:53 2016

@author: minxu

Question class for crawling and storing information of a question in zhihu.com.

features:
question title and topics, top answers and votes, popularity information, supports
both file and database storage type

constructor:
specify question id, session and optional MongoDB database object (default is None).
If database is specified, storage mode will be database instead of file

methods:
evaluate(): evaluate fields
flush(): flush all information for this question to file/database depending on 
the storage mode

fields:
    field = {
            'qid' : question_id,
            'url' : question_url,
            'anum' : answer_number,
            'title' : question_title,
            'question' : question_details,
            'labels' : [list_of_question_topic_labels],
            'answers' : [list_of_answers_struct {
                'agrees' : number_of_agrees,
                'text' : answer_text,
                'url' : answer_url,
                'aid' : answer_id
            }]
    }

"""
from bs4 import BeautifulSoup
import os
import os.path
import json
import pymongo

zhihu_url = "https://www.zhihu.com"
subdir = '/questions/'


class Question:
    
    def __init__(self, qid, session, db = None):
        self.url = zhihu_url + '/question/' + qid
        self.qid = qid
        self.session = session
        self.db = db
    
    #evaluate all fields from the responded html for this question
    def evaluate(self):
        if check_question(self.qid, self.db):
            return False
            
        connected = False
        while not connected:
            try:
                self.soup = BeautifulSoup(self.session.get(self.url).text)
                connected = True
            except:
                continue
        
        self.get_anum()
        self.get_title()
        self.get_question()
        self.get_labels()
        self.get_answers()
        return True
    
    #wrapper for flush all information for this question to file/database 
    #depending on the storage mode 
    def flush(self):
        if self.db is None:
            self.flush_to_file()
        else:
            self.flush_to_db()
    
    #flush data to database
    def flush_to_db(self):
        try:
            self.db.questions.insert_one(self.construct_data())        
        except pymongo.errors.DuplicateKeyError:
            return
    
    #flush data to file in json format
    def flush_to_file(self):
        json_dict = self.construct_data()
        with open(os.getcwd() + subdir + self.qid + '.json', 'w') as f:
            json.dump(json_dict, f, indent=4)
    
    #construct data in dictionary type
    def construct_data(self):
        data = {
            '_id' : self.qid, #for MongoDB
            'qid' : self.qid,
            'url' : self.url,
            'anum' : self.anum,
            'title' : self.title,
            'question' : self.question,
            'labels' : self.labels,
            'answers' : self.answers
        }
        return data
    
    #get number of answers
    def get_anum(self):
        self.anum = int(self.soup.find('h3', id = "zh-question-answer-num")['data-num'])
    
    #get the question title text
    def get_title(self):
        self.title = self.soup.find('h2', class_ = \
            "zm-item-title zm-editable-content").find(text = True).strip()
        
    #get the question details text
    def get_question(self):
        self.question = self.soup.find('div', id = "zh-question-detail"). \
            find('div', class_ = "zm-editable-content").text.strip()
    
    #get a list of topic labels associated
    def get_labels(self):
        self.labels = []
        ls = self.soup.find('div', class_ = "zm-tag-editor-labels zg-clear").findAll('a')
        for l in ls:
            self.labels.append(l.find(text = True))
    
    #get a list of answers structure, with number of agrees, text, url and id
    def get_answers(self):
        self.answers = []
        for a in self.soup.findAll('div', class_ = 'zm-item-answer  zm-item-expanded'):
            url = a.find('link', itemprop="url")['href']
            aid = url.split('/')[4]
            url = zhihu_url + url
            agrees = int(a.find('div', class_ = "zm-votebar").find('span', class_ = "count").text)
            text = a.find('div', class_ = "zm-editable-content clearfix").text
            answer = {
                'agrees' : agrees,
                'text' : text,
                'url' : url,
                'aid' : aid
            }
            self.answers.append(answer)

#check if this question object exists in database or file
def check_question(qid, db = None):
    if db is None:
        return os.path.exists(os.getcwd() + subdir + qid + '.json')
    else:
        return db.questions.find({'_id' : qid}).count() != 0
