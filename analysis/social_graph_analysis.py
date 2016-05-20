# -*- coding: utf-8 -*-
"""
Created on Wed May 18 15:14:06 2016

@author: minxu
"""
import itertools
import pymongo
client = pymongo.MongoClient()
db = client.zhihu

def first_order_connections(uid):
    u = db.users.find_one({'_id' : uid})
    nodes = [uid] + u['followees'] + u['followers']
    users = db.users.find({'_id' : {'$in' : nodes}})
    user_dict = {user['_id'] : (set(user['followees']), set(user['followers'])) for user in users}                
    nodes = list(user_dict)
    index_dict = dict(zip(nodes, range(len(nodes))))
    linkset = set()
    for (i, j) in itertools.combinations(nodes, 2):
        if i in user_dict[j][0]: #i is j's followees
            linkset.add((index_dict[j], index_dict[i])) #from j->i
        if i in user_dict[j][1]: #j is i's followers
            linkset.add((index_dict[i], index_dict[j])) #from i->j
    
    return nodes, linkset

def format_to_json(nodes, linkset):
    js_dict = dict()
    js_dict['nodes'] = [{'name' : db.users.find_one({'_id' : uid})['name']} for uid in nodes]
    js_dict['links'] = [{'source' : i, 'target' : j} for (i,j) in linkset]
    return js_dict

def get_first_order_connection_json(uid):
    u = db.users.find_one({'_id' : uid})
    if u is None:
        return None
    if 'first_order_social_graph' in u:
        return u['first_order_social_graph']
    else:
        nodes, linkset = first_order_connections(uid)
        js_dict = format_to_json(nodes, linkset)
        db.users.update_one( 
            {'_id' : uid},
            {'$set' : 
                {
                    'first_order_social_graph' : js_dict
                }
            }        
        )
        return js_dict