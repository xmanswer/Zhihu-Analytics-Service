# -*- coding: utf-8 -*-
"""
Created on Wed May 25 16:06:21 2016

@author: minxu
"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu

inner_uid = 0
for u in db.users.find():
    db.inneruid.insert_one({
        '_id' : inner_uid,
        'uid' : u['_id']
    })
    db.users.update_one(
            {'_id' : u['_id']},
            {'$set' : 
                {
                    'inner_id' : inner_uid
                }
            }        
        )
    
    inner_uid += 1

inner_qid = 0
for q in db.questions.find():
    print inner_qid
    db.innerqid.insert_one({
        '_id' : inner_qid,
        'qid' : q['_id']
    })
    db.questions.update_one(
        {'_id' : q['_id']},
        {'$set' : 
            {
                'inner_id' : inner_qid
            }
        }        
    )
    inner_qid += 1