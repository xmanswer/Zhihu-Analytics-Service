# -*- coding: utf-8 -*-
"""
Created on Sun May 08 16:36:25 2016

@author: minxu
"""

import pymongo
import jieba
import jieba.analyse
jieba.enable_parallel(10)
allowPos = ('ns', 'n', 'vn', 'v')

#K defines top K keywords, method can be extract_tags(tf-idf based) or textrank
def get_user_keywords(uid, field, K = 20, method = jieba.analyse.extract_tags, db):
    user = db.users.find_one({'_id' : uid})
    if user is not None:
        return method(t, user[field], topK = K, allowPos = allowPos)
    else:
        return None

#K defines top K keywords, method can be extract_tags(tf-idf based) or textrank
def get_question_keywords(qid, K = 20, method = jieba.analyse.extract_tags, db):
    question = db.questions.find({'_id' : uid})
    if question is not None:
        keywords = []
        title, detail = question['title'], question['question']
        t_words = jieba.cut(title + detail, cut_all = False)
        t_K = 1 + int(float(len(t_words)) * 0.2)
        t_words = method(' '.join(t_words), topK = t_K, allowPos = allowPos)
        keywords.extend(t_words)
        answers = question['answers']
        a_words = method(' '.join([a.text for a in answers]), topK = K, allowPos = allowPos)
        keywords.extend(a_words)
        return keywords

#create a new keywords field in the database for given user
def flush_user_keywords(uid, field, keywords, db):
    if keywords is not None:
        db.users.update_one(
            {'_id' : uid},
            {'$set' : 
                {
                    field + '_keywords' : keywords
                }
            }        
        )

def flush_question_keywords(qid, keywords, db):
    if keywords is not None:
        db.questions.update_one(
            {'_id' : qid},
            {'$set' : 
                {
                    'keywords' : keywords
                }
            }        
        )

def generate_user_keywords(K = 20, method = jieba.analyse.extract_tags, db):
    for u in db.users.find(no_cursor_timeout=True):
        k1 = get_user_keywords(u, 'answers', K, method, db)
        k2 = get_user_keywords(u, 'timelines', K, method, db)
        flush_user_keywords(u, 'answers', k1, db)
        flush_user_keywords(u, 'timelines', k1, db)

def generate_question_keywords(K = 20, method = jieba.analyse.extract_tags, db):
    for q in db.questions.find(no_cursor_timeout=True):
        k = get_question_keywords(q, K, method, db)
        flush_question_keywords(u, k, db)