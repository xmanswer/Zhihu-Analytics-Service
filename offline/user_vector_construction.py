# -*- coding: utf-8 -*-
"""
Created on Wed May 25 16:19:11 2016

@author: minxu
"""
import math
import pymongo
client = pymongo.MongoClient()
db = client.zhihu

dictionary = db.dictionary.find_one({'_id' : 'dict'})['value']

for u in db.users.find():
    timelines_keywords = u['timelines_keywords']
    answers_keywords = u['answers_keywords']
    keywords_scores = dict()
    keywords_vectors = dict()
    
    for i, w in enumerate(timelines_keywords):
        if w in keywords_scores:
            keywords_scores[w] += len(timelines_keywords) - i
        else:
            keywords_scores[w] = len(timelines_keywords) - i
    
    for i, w in enumerate(answers_keywords):
        if w in keywords_scores:
            keywords_scores[w] += len(answers_keywords) - i
        else:
            keywords_scores[w] = len(answers_keywords) - i    
    
    if len(keywords_scores) > 0:
        max_w = max(keywords_scores, key=keywords_scores.get)
        min_w = min(keywords_scores, key=keywords_scores.get)
        
    for w in keywords_scores:
        if w in dictionary:
            keywords_vectors[str(dictionary[w])] = math.sqrt((keywords_scores[w] - \
            keywords_scores[min_w] + 1.0) / (keywords_scores[max_w] - keywords_scores[min_w] + 1.0))
    
    db.users.update_one(
            {'_id' : u['_id']},
            {'$set' : 
                {
                    'vector' : keywords_vectors
                }
            }        
        )