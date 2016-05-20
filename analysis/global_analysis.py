# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:12:49 2016

@author: minxu

Analyze global general statistics such as top users/questions, total of
agrees, thanks, followers, followees

Also evaluate distribution statistics for all users

"""
import heapq
import pymongo
client = pymongo.MongoClient()
db = client.zhihu

#global statistics
db.glob.insert_one({
        '_id' : 'global_par',
        'name' : 'global_par',
        'value' : list(db.users.aggregate([
            {
                '$group' : {
                    '_id' : None,
                    'total_thanks' : {'$sum' : '$thanks'},
                    'average_thanks' : {'$avg' : '$thanks'},
                    'total_agrees' : {'$sum' : '$agrees'},
                    'average_agrees' : {'$avg' : '$agrees'},
                    'average_followees' : {'$avg' : '$followees_num'},
                    'average_followers' : {'$avg' : '$followers_num'}
                }
            }
        ]))[0]
})

#top 10 users/questions/answers
db.glob.insert_one({
    '_id' : 'top_10_thanks',
    'name' : 'top_10_thanks',
    'value' : [u['_id'] for u in db.users.find().sort([('thanks', -1)]).limit(10)]
})

db.glob.insert_one({
    '_id' : 'top_10_agrees',
    'name' : 'top_10_agrees',
    'value' : [u['_id'] for u in db.users.find().sort([('agrees', -1)]).limit(10)]
})

db.glob.insert_one({
    '_id' : 'top_10_followers',    
    'name' : 'top_10_followers',
    'value' : [u['_id'] for u in db.users.find().sort([('followers_num', -1)]).limit(10)]
})

db.glob.insert_one({
    '_id' : 'top_10_followees',
    'name' : 'top_10_followees',
    'value' : [u['_id'] for u in db.users.find().sort([('followees_num', -1)]).limit(10)]
})

db.glob.insert_one({
    '_id' : 'top_10_questions',
    'name' : 'top_10_questions',
    'value' : list(db.questions.find().sort([('anum', -1)]).limit(10))
})

db.glob.insert_one({
    '_id' : 'top_10_answers',
    'name' : 'top_10_answers',
    'value' : list(db.questions.aggregate([
        {'$unwind' : '$answers'},
        {'$sort' : {'answers.agrees' : -1}},
        {'$limit' : 10}
    ]))
})

db.glob.insert_one({
    '_id' : 'top_10_pageRank',
    'name' : 'top_10_pageRank',
    'value' : [u['_id'] for u in db.users.find().sort([('pageRank', -1)]).limit(10)]
})

db.glob.insert_one({
    '_id' : 'top_10_quality',
    'name' : 'top_10_quality',
    'value' : [u['_id'] for u in db.users.find().sort([('quality', -1)]).limit(10)]
})


#top question keywords
keywords_dict = dict()

for q in db.questions.find():
    if 'keywords' in q:
        for i in range(len(q['keywords'])):
            kw = q['keywords'][i]
            if kw in keywords_dict:
                keywords_dict[kw] += 1.0 / float(i + 1)
            else:
                keywords_dict[kw] = 1.0 / float(i + 1)
keys_of_keys = heapq.nlargest(100, keywords_dict, key=keywords_dict.get)
db.glob.insert_one({
    '_id' : 'top_keywords',
    'name' : 'top_keywords',
    'value' : keys_of_keys
})

#distribution of user agrees and followers
total_user = db.users.count()
x = [int(i * 1.0 / 100 * total_user) for i in range(1, 100)]
x.insert(0, 0)
yagrees = []
yfollowers = []
yfollowees = []
ythanks = []
yPageRank = []
yquality = []
cnt = 0
for u in db.users.find():
    yfollowers.append(u['followers_num'])
    yagrees.append(u['agrees'])
    yfollowees.append(u['followees_num'])
    ythanks.append(u['thanks'])
    yPageRank.append(u['pageRank'])
    yquality.append(u['quality'])

yfollowers.sort(reverse=True)
yagrees.sort(reverse=True)
yfollowees.sort(reverse=True)
ythanks.sort(reverse=True)
yPageRank.sort(reverse=True)
yquality.sort(reverse=True)

yfollowers = [yfollowers[i]+1 for i in x]
yagrees = [yagrees[i]+1 for i in x]
yfollowees = [yfollowees[i]+1 for i in x]
ythanks = [ythanks[i]+1 for i in x]
yPageRank = [yPageRank[i] + 1e-6 for i in x]
yquality = [yquality[i] + 1e-6 for i in x]


db.glob.insert_one({
    '_id' : 'distributions',
    'name' : 'distributions',
    'value' : {
        'agrees' : yagrees,
        'followers' : yfollowers,
        'thanks' : ythanks,
        'followees' : yfollowees,
        'pageRank' : yPageRank,
        'quality' : yquality
    }
})
