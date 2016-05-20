# -*- coding: utf-8 -*-
"""
Created on Fri May 20 14:14:59 2016

@author: minxu

quality score is defined as average_answer_length * sum_of_agrees_and thanks / num_of_followers

it is a measure of how good the user is at generating good answers

"""
import math
import pymongo
client = pymongo.MongoClient()
db = client.zhihu

users = dict()

for u in db.users.find():
    if len(u['answers']) > 0:
        average_answer_length = sum([len(a['text']) for a in u['answers']]) / len(u['answers'])
    else:
        average_answer_length = 0
    agrees = u['agrees']
    thanks = u['thanks']
    followers_num = len(u['followers'])
    if followers_num == 0:
        followers_num = db.glob.find_one({'name' : 'global_par'})['value']['average_followers']
    users[u['uid']] = average_answer_length * (agrees + thanks) / followers_num

#update users dictionary, with value as pr score
def update_value(f, d):
    for k,v in d.iteritems():
        d[k] = f(v)
    
update_value(lambda x : math.log(x+1), users)
max_pr, min_pr = max(users.values()), min(users.values())
update_value(lambda x :(x - min_pr) / (max_pr - min_pr), users)

#dump to db
for u in users:
    db.users.update_one( 
            {'_id' : u},
            {'$set' : 
                {
                    'quality' : users[u]
                }
            }        
    )