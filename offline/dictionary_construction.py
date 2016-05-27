# -*- coding: utf-8 -*-
"""
Created on Fri May 20 16:32:30 2016

@author: minxu
"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu
db.dictionary.remove()

dictionary = dict()
word_freq = dict()
word_df = dict()
index, cnt = 0, 0
for q in db.questions.find():
    if cnt % 1000 == 0:
        print cnt, index
    if 'keywords' in q:
        df_set = set()
        for word in q['keywords']:
            df_set.add(word)
            if word not in dictionary: #assign index and first count
                dictionary[word] = index
                word_freq[str(index)] = 1
                index += 1
            else: #increase glob count for word
                word_freq[str(dictionary[word])] += 1
                
        for word in df_set:
            if word in word_df:
                word_df[str(dictionary[word])] += 1
            else:
                word_df[str(dictionary[word])] = 1
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

db.dictionary.insert_one({
    '_id' : 'df',
    'value' : word_df
})