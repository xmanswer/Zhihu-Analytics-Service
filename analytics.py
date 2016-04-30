# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 12:15:28 2016

@author: minxu
"""
from bs4 import BeautifulSoup
import requests
import Person
import zhihu_login
import jieba
import jieba.analyse
import threading
import re

class userThread (threading.Thread):
    def __init__(self, uid):
        threading.Thread.__init__(self)
        self.uid = uid

    def run(self):
        analyze_user(self.uid)

zhihu_url = "https://www.zhihu.com"
profile_url = zhihu_url + "/settings/profile"
profile = zhihu_login.session.get(profile_url).text

userlist = ["min-xu-26", "song-shu-shan-lao-nong", "zhengkun-dai", "bai-xiao-yu-95", "chen-woo","a-la-ding-jiang-jun"]
userdict = dict()
userworddict =dict()

def analyze_user(uid):
    person = Person.Person(uid, zhihu_login.session)
    userdict[uid] = person
    all_words = ""
    connected = False
    while not connected:
        try:
            answers = person.get_timelines()
            connected = True
        except requests.ConnectionError:
            continue
        else:
            connected = True

    for i in answers:
        all_words = all_words + i
    userworddict[uid] = ','.join(jieba.analyse.extract_tags(all_words, topK=50, withWeight=False, allowPOS=()))


#soup = BeautifulSoup(profile)
#for a in soup.findAll('a'):
#    if '/people/' in a['href']:
#        my_id = a['href'][len('/people/') :]
#        break

threads = []

for uid in userlist:
    t = userThread(uid)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

for user in userworddict:
    print user + "'s most frequent words:"
    print userworddict[user]
    print '\n'


