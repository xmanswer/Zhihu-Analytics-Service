# -*- coding: utf-8 -*-
"""
Created on Mon May 23 06:59:27 2016

@author: minxu
"""

import pymongo
client = pymongo.MongoClient()
db = client.zhihu

print 'users counts: ' + str(db.users.count())
non_ukeywords = db.users.aggregate([{'$group':{'_id':{'$gt':["$timelines_keywords", 'null']}, 'count':{'$sum':1}}}])
print 'non keywords for users: ' + str(list(non_ukeywords)[0])
print 'questions counts: ' + str(db.questions.count())
non_qkeywords = db.questions.aggregate([{'$group':{'_id':{'$gt':["$keywords", 'null']}, 'count':{'$sum':1}}}])
print 'non keywords for questions: ' + str(list(non_qkeywords)[0])
