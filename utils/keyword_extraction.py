# -*- coding: utf-8 -*-
"""
Created on Sun May 08 16:36:25 2016

@author: minxu
"""

import jieba
import jieba.analyse
#jieba.enable_parallel(8)
allowPOS = ('ns', 'n', 'vn', 'v')

#K defines top K keywords, method can be extract_tags(tf-idf based) or textrank
def get_user_keywords(uid, field, db, K = 20, method = jieba.analyse.extract_tags):
    user = db.users.find_one({'_id' : uid})
    if user is not None:
        return method(' '.join([t['text'] for t in user[field]]), topK = K, allowPOS = allowPOS)
    else:
        return None

#K defines top K keywords, method can be extract_tags(tf-idf based) or textrank
def get_question_keywords(qid, db, K = 20, method = jieba.analyse.extract_tags):
    question = db.questions.find_one({'_id' : qid})
    if question is not None:
        keywords = []
        title, detail = question['title'], question['question']
        t_words = list(jieba.cut(title + detail, cut_all = False))
        t_K = 1 + int(float(len(t_words)) * 0.2)
        t_words = method(' '.join(t_words), topK = t_K, allowPOS = allowPOS)
        keywords.extend(t_words)
        answers = question['answers']
        a_words = method(' '.join([a['text'] for a in answers]), topK = K, allowPOS = allowPOS)
        keywords.extend(a_words)
        return keywords
    else:
        return None

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

def user_kw_wrapper((uid, db, K, method)):
    u = db.users.find_one({'_id' : uid})
    if u is None:
        return
    if 'answers_keywords' not in u or 'timelines_keywords' not in u:
        k1 = get_user_keywords(u['_id'], 'answers', db, K, method)
        k2 = get_user_keywords(u['_id'], 'timelines', db, K, method)
        flush_user_keywords(u['_id'], 'answers', k1, db)
        flush_user_keywords(u['_id'], 'timelines', k2, db)
        print 'keywords extracted for user ' + u['_id']
        u = None

def question_kw_wrapper((qid, db, K, method)):
    q = db.questions.find_one({'_id' : qid})
    if q is None:
        return
    if 'keywords' not in q:
        k1 = get_question_keywords(q['_id'], db, K, method)
        flush_question_keywords(q['_id'], k1, db)
        print 'keywords extracted for question ' + q['_id']
        q = None
    
def generate_user_keywords(db, threadpool = None, K = 20, method = jieba.analyse.extract_tags):
    if threadpool is None:
        for u in db.users.find(no_cursor_timeout=True):
            user_kw_wrapper(u['_id'], db, K, method)
    else:
        args = [(u['_id'], db, K, method) for u in db.users.find(no_cursor_timeout=True)]
        threadpool.map(user_kw_wrapper, args)

def generate_question_keywords(db, threadpool = None, K = 20, method = jieba.analyse.extract_tags):
    if threadpool is None:    
        for q in db.questions.find(no_cursor_timeout=True):
            question_kw_wrapper(q['_id'], db, K, method)
    else:
        args = [(q['_id'], db, K, method) for q in db.questions.find(no_cursor_timeout=True)]
        threadpool.map(question_kw_wrapper, args)        

        
