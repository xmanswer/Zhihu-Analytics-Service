# -*- coding: utf-8 -*-
"""
Created on Wed May 18 15:14:06 2016

@author: minxu
"""
import itertools
import pymongo
client = pymongo.MongoClient()
db = client.zhihu

def first_order_connections(u):
    uid = u['uid']
    nodes = [uid] + u['followees'] + u['followers']
    users = db.users.find({'_id' : {'$in' : nodes}})
    user_dict = {user['_id'] : (set(user['followees']), set(user['followers'])) for user in users}                
    nodes = list(user_dict)
    index_dict = dict(zip(nodes, range(len(nodes))))
    linkset = set()
    for (i, j) in itertools.combinations(nodes, 2):
        if i in user_dict[j][0] and i in user_dict[j][1]: #dual connection
            linkset.add((index_dict[j], index_dict[i], 5)) #from j->i
            linkset.add((index_dict[i], index_dict[j], 5)) #from i->j
        elif i in user_dict[j][1]: #j is i's followers
            linkset.add((index_dict[i], index_dict[j], 1)) #from i->j
        elif i in user_dict[j][0]: #i is j's followees
            linkset.add((index_dict[j], index_dict[i], 1)) #from j->i
    
    return nodes, linkset

def get_group(uid, core_user):
    if uid == core_user['_id']: #myself
        return 3
    elif uid in core_user['followees'] and uid in core_user['followers']: #dual connection
        return 2
    elif uid in core_user['followees']: #only followees
        return 1
    else: #only followers
        return 0

def format_to_json(nodes, linkset, core_user):
    js_dict = dict()
    js_dict['nodes'] = [{'name' : db.users.find_one({'_id' : uid})['name'], 'group' : get_group(uid, core_user)} for uid in nodes]
    js_dict['links'] = [{'source' : i, 'target' : j, 'value' : v} for (i,j,v) in linkset]
    return js_dict

def get_first_order_connection_json(uid):
    u = db.users.find_one({'_id' : uid})
    if u is None:
        return None
    if 'first_order_social_graph' in u:
        return u['first_order_social_graph']
    else:
        nodes, linkset = first_order_connections(u)
        js_dict = format_to_json(nodes, linkset, u)
        db.users.update_one( 
            {'_id' : uid},
            {'$set' : 
                {
                    'first_order_social_graph' : js_dict
                }
            }        
        )
        return js_dict