# -*- coding: utf-8 -*-
"""
Created on Tue May 17 13:04:08 2016

@author: minxu

construct username database where key (_id) is username, and value
is a list of user ids. This is for fast searching of username

"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu

undict = dict()
for u in db.users.find():
    un = u['name']
    if un not in undict:
        undict[un] = [u['_id']]
    else:
        undict[un].append(u['_id'])
        

for k, v in undict.iteritems():
    db.usernames.insert_one({
        '_id' : k,
        'uids' : v
    })