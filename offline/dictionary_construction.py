# -*- coding: utf-8 -*-
"""
Created on Fri May 20 16:32:30 2016

@author: minxu
"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu

dictionary = dict()
word_freq = dict()
index, cnt = 0, 0
for q in db.questions.find():
    if cnt % 1000 == 0:
        print cnt, index
    if 'keywords' in q:
        for word in q['keywords']:
            if word not in dictionary: #assign index and first count
                dictionary[word] = index
                word_freq[word] = 1
                index += 1
            else: #increase glob count for word
                word_freq[word] += 1
    cnt += 1

print 'found all keywords'
db.dictionary.insert_one({
    '_id' : 'dict',
    'value' : dictionary
})

db.dictionary.insert_one({
    '_id' : 'ctf',
    'value' : word_freq
})