# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 13:02:27 2016

@author: minxu
"""
from bs4 import BeautifulSoup
import re
import json

zhihu_url = "https://www.zhihu.com"
friends_url_dict = {'/followees' : 'ProfileFolloweesListV2', 
                    '/followers' : 'ProfileFollowersListV2'}

TOP_INTERESTS = 100

class Person:

    def __init__(self, uid, session):
        self.uid = uid
        self.session = session
        self.url = zhihu_url + '/people/' + uid
        
        personal_page = session.get(self.url).text
        personal_soup = BeautifulSoup(personal_page)
        self.followees_num, self.followers_num  = self.get_friends_num(personal_soup)
        self.agrees, self.thanks = self.get_agrees(personal_soup)
        self.followees = self.get_friends(personal_page, self.followees_num, '/followees')
        self.followers = self.get_friends(personal_page, self.followers_num, '/followers')
        
    def get_friends_num(self, soup):
        alla = soup.find("div", class_="zm-profile-side-following zg-clear").findAll("a")
        return int(alla[0].strong.string), int(alla[1].strong.string)
        
    def get_agrees(self, soup):
        agrees = int(soup.find("span", class_="zm-profile-header-user-agree").strong.string)
        thanks = int(soup.find("span", class_="zm-profile-header-user-thanks").strong.string)
        return agrees, thanks
    
    def get_friends(self, page, num, friend_type):
        furl = self.url + friend_type
        fpage = self.session.get(furl).text
        fsoup = BeautifulSoup(fpage)
        flist = []
        for i in xrange((num - 1) / 20 + 1):
            if i == 0:
                ul = fsoup.find_all("h2", class_="zm-list-content-title")
                for j in xrange(min(self.followees_num, 20)):
                    flist.append(ul[i].a['data-tip'][4:])
            else:
                post_url = "http://www.zhihu.com/node/" + friends_url_dict[friend_type]
                _xsrf = fsoup.find("input", attrs={'name': '_xsrf'})["value"]
                offset = i * 20
                hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", fpage)[0]
                params = json.dumps({"offset": offset, "order_by": "created", "hash_id": hash_id})
                data = {
                    '_xsrf': _xsrf,
                    'method': "next",
                    'params': params
                }
                header = {
                    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                    'Host': "www.zhihu.com",
                    'Referer': furl
                }
                
                r_post = self.session.post(post_url, data=data, headers=header)
                extenedlist = r_post.json()["msg"]
                
                for j in xrange(min(num - i * 20, 20)):
                    soup = BeautifulSoup(extenedlist[j], "lxml")
                    flist.append(soup.find("h2", class_="zm-list-content-title").a['data-tip'][4:])
        
        return flist

    def get_answers(self):
        asoup = BeautifulSoup(self.session.get(self.url + '/answers?page=1').text)
        pagesection = asoup.find("div",  class_="zm-invite-pager")
        pagesize = 0
        answers = []
        if pagesection == None:
            pagesize = 1
        else:
            spanall = pagesection.findAll("span")
            for span in spanall:
                if span.a != None and span.a.string.isdigit():
                    pagesize = max(pagesize, int(span.a.string))
                
        for i in range(1, pagesize + 1):
            asoup = BeautifulSoup(self.session.get(self.url + '/answers?page=' + str(i)).text)
            for answer in asoup.findAll('textarea', class_="content"):
                answers.append(answer.string)
        
        return answers
    
#    def get_interests(self):
        