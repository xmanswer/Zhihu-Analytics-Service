# -*- coding: utf-8 -*-
"""
Created on Fri May 20 10:42:47 2016

@author: minxu
"""

import itertools
import pymongo
client = pymongo.MongoClient()
db = client.zhihu
ITER = 100
d = 0.85

total = db.users.count()
users = dict()

class User:
    def __init__(self, uid, pr_cur, pr_next, followers, followees):
        self.uid = uid
        self.pr_cur = pr_cur
        self.pr_next = pr_next
        self.followers = followers
        self.followees = followees

for u in db.users.find():
    uid = u['_id']
    users[uid] = User(uid, 1.0/total, 0, u['followers'], u['followees'])

for Iter in range(ITER):
    print 'Iteration ' + str(Iter)
    for u in users:
        users[u].pr_next = (1 - d) / total + d * sum([users[i].pr_cur / len(users[i].followees) for i in users[u].followers])
    for u in users:
        users[u].pr_cur = users[u].pr_next
        users[u].pr_next = 0

uscore = {users[u].uid : users[u].pr_cur for u in users}

topusers = heapq.nlargest(10, users, key=uscore.get)