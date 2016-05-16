# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:12:49 2016

@author: minxu
"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu

#global statistics
db.glob.insert_one({
        'name' : 'global_par',
        'value' : list(db.users.aggregate([
            {
                '$group' : {
                    '_id' : None,
                    'total_thanks' : {'$sum' : '$thanks'},
                    'average_thanks' : {'$avg' : '$thanks'},
                    'total_agrees' : {'$sum' : '$agrees'},
                    'average_agrees' : {'$avg' : '$agrees'},
                    'average_followees' : {'$avg' : '$followees_num'}
                    'average_followers' : {'$avg' : '$followers_num'}
                }
            }
        ]))[0]
})

#top 10 users/questions/answers
db.glob.insert_one({
    'name' : 'top_10_thanks',
    'value' : list(db.users.find().sort([('thanks', -1)]).limit(10))
})

db.glob.insert_one({
    'name' : 'top_10_agrees',
    'value' : list(db.users.find().sort([('agrees', -1)]).limit(10))
})

db.glob.insert_one({
    'name' : 'top_10_followers',
    'value' : list(db.users.find().sort([('followers_num', -1)]).limit(10))
})

db.glob.insert_one({
    'name' : 'top_10_followees',
    'value' : list(db.users.find().sort([('followees_num', -1)]).limit(10))
})

db.glob.insert_one({
    'name' : 'top_10_questions',
    'value' : list(db.questions.find().sort([('anum', -1)]).limit(10))
})

db.glob.insert_one({
    'name' : 'top_10_answers',
    'value' : list(db.questions.aggregate([
        {'$unwind' : '$answers'},
        {'$sort' : {'answers.agrees' : -1}},
        {'$limit' : 10}
    ]))
})

"""
top keywords, awaiting data to be loaded
"""
