# -*- coding: utf-8 -*-
"""
Created on Wed May 25 16:36:46 2016

@author: minxu
"""

import math
import pymongo
client = pymongo.MongoClient()
db = client.zhihu

dictionary = db.dictionary.find_one({'_id' : 'dict'})['value']

for q in db.questions.find():
    keywords = q['keywords']
    keywords_scores = dict()
    keywords_vectors = dict()
    
    for i, w in enumerate(keywords):
        if w in keywords_scores:
            keywords_scores[w] += len(keywords) - i
        else:
            keywords_scores[w] = len(keywords) - i
            
    if len(keywords_scores) > 0:
        max_w = max(keywords_scores, key=keywords_scores.get)
        min_w = min(keywords_scores, key=keywords_scores.get)
    
    for w in keywords_scores:
        if w in dictionary:
            keywords_vectors[str(dictionary[w])] = math.sqrt((keywords_scores[w] - \
            keywords_scores[min_w] + 1.0) / (keywords_scores[max_w] - keywords_scores[min_w] + 1.0))
    
    db.questions.update_one(
            {'_id' : q['_id']},
            {'$set' : 
                {
                    'vector' : keywords_vectors
                }
            }        
        )