# -*- coding: utf-8 -*-
"""
Created on Mon May 23 10:40:45 2016

@author: minxu
"""
import sys
import os
main_dir = os.path.realpath('..')
sys.path.append(main_dir)

import pymongo
import scipy as sp
import numpy as np
from functools import partial
import math
import heapq
from multiprocessing.dummy import Pool

client = pymongo.MongoClient()
db = client.zhihu

#if matrix file not dumped, create the matrix files for questions and users
#each row is a user/question, each column is a word
if not os.path.exists(main_dir + '/offline/user_matrix'):
    dictionary = db.dictionary.find_one({'_id' : 'dict'})['value']
    df = db.dictionary.find_one({'_id' : 'df'})['value']
    N = len(dictionary)
    Mu = db.users.count()
    Mq = list(db.questions.aggregate([{'$group' :{'_id' : None, 'count' : {'$sum' : 1}}}]))[0]['count']

    user_matrix = sp.sparse.lil_matrix((Mu, N))
    question_matrix = sp.sparse.lil_matrix((Mq, N))
    
    def map_to_matrix(word, score, innerid, matrix):
        matrix[innerid, int(word)] = score * \
        math.log(1 + Mq/df[word])
    
    ucnt = 0
    for user in db.users.find():
        if ucnt % 1000 == 0:
            print ucnt
        mapfunc = partial(map_to_matrix, innerid = user['inner_id'], matrix=user_matrix)
        map(mapfunc, user['vector'].keys(), user['vector'].values())
    
    #    for w_id, score in user['vector'].items():
    #        user_matrix[user['inner_id'], int(w_id)] = score
        ucnt += 1
    
    qcnt = 0
    for question in db.questions.find():
        if qcnt % 1000 == 0:
            print qcnt
        mapfunc = partial(map_to_matrix, innerid = question['inner_id'], matrix=question_matrix)
        map(mapfunc, question['vector'].keys(), question['vector'].values())
    #    for w_id, score in question['vector'].items():
    #        question_matrix[question['inner_id'], int(w_id)] = score
        qcnt += 1
    
    with open(main_dir + '/offline/user_matrix', 'w') as f:
        sp.io.mmwrite(f, user_matrix)
    
    with open(main_dir + '/offline/question_matrix', 'w') as f:
        sp.io.mmwrite(f, question_matrix)
else: #if files exist, load the matrices
    with open(main_dir + '/offline/user_matrix') as f:
        user_matrix = sp.io.mmread(f)
    with open(main_dir + '/offline/question_matrix') as f:
        question_matrix = sp.io.mmread(f)
    
    Mu, N = user_matrix.shape
    Mq, N = question_matrix.shape

#produce recommendation of top 10 questions for each user
user_matrix = user_matrix.tocsr()
question_matrix = question_matrix.tocsr()
question_matrix_trans = question_matrix.transpose()

batchsize = 500
startlist = range(0, Mu, batchsize)
endlist = [min([i + batchsize, Mu]) for i in startlist]

user_recommend_dict = dict()

inneruid_dict = {i['_id'] : i['uid'] for i in db.inneruid.find({'_id' : {'$in' : range(0, Mu)}})}
innerqid_dict = {i['_id'] : i['qid'] for i in db.innerqid.find({'_id' : {'$in' : range(0, Mq)}})}


for start, end in zip(startlist, endlist):
    print 'start ' + str(start)
    uqs = user_matrix[start:end,:] * question_matrix_trans
    pool = Pool(8)

    def get_for_one_user(u):
        uid = inneruid_dict[u]
        user = db.users.find_one({'_id' : uid})
        uq = uqs[u - start, :]
        d = zip(uq.indices, uq.data)
        topk = heapq.nlargest(400, d, key=lambda tup : tup[1])
        qlist = []
        qset = set(user['questions'])
        for q_inner in topk:
            if len(qlist) > 10: break
            q_outer = innerqid_dict[q_inner[0]]
            if q_outer not in qset:
                qlist.append(q_outer)
        
        user_recommend_dict[user['_id']] = qlist
        print u
    
    try:
        pool.map(get_for_one_user, range(start, end))
        pool.close()
        pool.join()
    except Exception:
        pool = Pool(8)
        pool.map(get_for_one_user, range(start, end))
        pool.close()
        pool.join()        


for uid in user_recommend_dict:
    db.users.update_one(
        {'_id' : uid},
        {'$set' : 
            {
                'top_questions' : user_recommend_dict[uid]
            }
        }        
    )

#produce recommendation of top 10 users for each user









