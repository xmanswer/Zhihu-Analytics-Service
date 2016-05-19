# -*- coding: utf-8 -*-
"""
Created on Wed May 18 15:17:53 2016

@author: minxu
"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu

#initialze followers list for each users
userset = set()
for u in db.users.find():
    userset.add(u['_id'])
    db.users.update_one(
        {'_id' : u['_id']},
        {'$set' : 
            {
                'followers' : []
            }
        }        
    )

print 'update followers....'
#update each user's followee's follower
for u in db.users.find():
    uid = u['uid']
    for fee in u['followees']:
        if fee in userset:
            db.users.update_one(
                {'_id' : fee},
                {'$push' : 
                    {
                        'followers' : uid
                    }
                }        
            )