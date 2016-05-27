# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:02:18 2016

@author: minxu
"""

from snownlp import SnowNLP
import pymongo
client = pymongo.MongoClient()
db = client.zhihu

def get_sentiment(answer):
    text = answer['text']
    s = SnowNLP(text)
    return s.sentiments

for q in db.questions.find():
    answer_sentiments = map(get_sentiment, q['answers'])
    question_sentiment = SnowNLP(q['title'] + q['question']).sentiments
    db.questions.update_one(
        {'_id' : q['_id']},
        {'$set' : 
            {
                'answer_sentiments' : answer_sentiments,
                'question_sentiment' : question_sentiment
            }
        }        
    )