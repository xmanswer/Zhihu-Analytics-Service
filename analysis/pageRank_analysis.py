# -*- coding: utf-8 -*-
"""
Created on Fri May 20 10:42:47 2016

@author: minxu

PageRank is a measure of user authority, generally, a user has higher PageRank 
score tends to have more powerful in-link (followers) who has less out-link

A series random walk algorithm is used to evaluate PageRank
"""

import heapq
import pymongo
import math
client = pymongo.MongoClient()
db = client.zhihu
ITER = 100
d = 0.85

total = db.users.count()
users = dict()

#helper class for storing user info
class User:
    def __init__(self, uid, pr_cur, pr_next, followers, followees_num):
        self.uid = uid
        self.pr_cur = pr_cur
        self.pr_next = pr_next
        self.followers = followers
        self.followees_num = followees_num

#create user dictionary
users = {u['_id'] : User(u['_id'], 1.0/total, 0, u['followers'], len(u['followees'])) for u in db.users.find()}

#map func for calculate pageRank score for one iteration
def pr_map1(u):
    users[u].pr_next = (1 - d) / total + d * sum([users[i].pr_cur / users[i].followees_num for i in users[u].followers])

#map func for update the pageRank score for each user
def pr_map2(u):
    users[u].pr_cur = users[u].pr_next
    users[u].pr_next = 0

uidlist = [u for u in users]

#iteratively update pageRank score
for Iter in range(ITER):
    map(pr_map1, uidlist)
    map(pr_map2, uidlist)

#update users dictionary, with value as pr score
def update_value(f, d):
    for k,v in d.iteritems():
        d[k] = f(v)

#soften using log and normalize to between 0 and 1
update_value(lambda x : math.log(x.pr_cur), users)
max_pr, min_pr = max(users.values()), min(users.values())
update_value(lambda x : (x - min_pr) / (max_pr - min_pr), users)

#dump to db
for u in users:
    db.users.update_one( 
            {'_id' : u},
            {'$set' : 
                {
                    'pageRank' : users[u]
                }
            }        
    )
