# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 12:15:28 2016

@author: minxu
"""
from bs4 import BeautifulSoup
import Person
import zhihu_login
import jieba
import jieba.analyse
import threading

class userThread (threading.Thread):
    def __init__(self, uid):
        threading.Thread.__init__(self)
        self.uid = uid

    def run(self):
        analyze_user(self.uid)

zhihu_url = "https://www.zhihu.com"
profile_url = zhihu_url + "/settings/profile"
profile = zhihu_login.session.get(profile_url).text

userlist =["song-shu-shan-lao-nong"] # ["song-shu-shan-lao-nong", "zhengkun-dai", "bai-xiao-yu-95", "chen-woo","a-la-ding-jiang-jun"]
userdict = dict()
userworddict =dict()

def analyze_user(uid):
    person = Person.Person(uid, zhihu_login.session)
    all_words = ""
    answers = person.get_answers()
    for i in answers:
        all_words = all_words + i
    
    userdict[uid] = person
    userworddict[uid] = jieba.analyse.extract_tags(all_words, topK=20, withWeight=False, allowPOS=())


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
    for w in userworddict[user]:
        print w
    
    print '\n\n'

