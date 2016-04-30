# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 13:02:27 2016

@author: minxu

A Person class for user information crawled from zhihu.com

"""
from bs4 import BeautifulSoup
import re
import json

zhihu_url = "https://www.zhihu.com"
friends_url_dict = {'/followees' : 'ProfileFolloweesListV2', 
                    '/followers' : 'ProfileFollowersListV2'}

TOP = 300

class Person:

    def __init__(self, uid, session):
        self.uid = uid
        self.session = session
        self.url = zhihu_url + '/people/' + uid
        
        personal_page = session.get(self.url).text
        self.personal_soup = BeautifulSoup(personal_page)
        self.followees_num, self.followers_num  = self.get_friends_num(self.personal_soup)
        self.agrees, self.thanks = self.get_agrees(self.personal_soup)
        self.followees = self.get_friends(personal_page, self.followees_num, '/followees')
        self.followers = self.get_friends(personal_page, self.followers_num, '/followers')
    
    #get total number of followees and followers
    def get_friends_num(self, soup):
        alla = soup.find("div", class_="zm-profile-side-following zg-clear").findAll("a")
        return int(alla[0].strong.string), int(alla[1].strong.string)
    
    #get total number of agrees and thanks received
    def get_agrees(self, soup):
        agrees = int(soup.find("span", class_="zm-profile-header-user-agree").strong.string)
        thanks = int(soup.find("span", class_="zm-profile-header-user-thanks").strong.string)
        return agrees, thanks
    
    #get friends (followers or followees) list of user ids
    def get_friends(self, page, num, friend_type):
        furl = self.url + friend_type
        fpage = self.session.get(furl).text
        fsoup = BeautifulSoup(fpage)
        flist = []
        for i in xrange((num - 1) / 20 + 1):
            if i == 0: #the first 20 users
                ul = fsoup.find_all("h2", class_="zm-list-content-title")
                for j in xrange(min(num, 20)):
                    flist.append(ul[j].a['data-tip'][4:])
            else: #more users, need to specify offsets to post request
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
        
    #get all answer texts, return a list of answer texts
    def get_answers(self):
        asoup = BeautifulSoup(self.session.get(self.url + '/answers?page=1').text)
        pagesection = asoup.find("div",  class_="zm-invite-pager")
        pagesize = 0
        answers = []
        
        #get number of pages first
        if pagesection == None:
            pagesize = 1
        else:
            spanall = pagesection.findAll("span")
            for span in spanall:
                if span.a != None and span.a.string.isdigit():
                    pagesize = max(pagesize, int(span.a.string))
        
        #get answer texts for each page
        for i in range(1, pagesize + 1):
            asoup = BeautifulSoup(self.session.get(self.url + '/answers?page=' + str(i)).text)
            for answer in asoup.findAll('textarea', class_="content"):
                answers.append(re.sub('<[^>]+>', '', answer.string)) #filter <garbage>
        
        return answers
    
    #get timeline texts up to a certain number (specified by TOP), return a list of them
    def get_timelines(self):
        soup = self.personal_soup
        timelines = []
        total = 0
        
        #construct post method for getting timelines, start_time is the first data_time
        post_url = self.url + "/activities"
        _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
        start_time = soup.find("div", attrs={'class':'zm-profile-section-item zm-item clearfix'})["data-time"]

        data = {
            'start': start_time,
            '_xsrf': _xsrf,
        }
        header = {
            'Host': "www.zhihu.com",
            'Referer': self.url,
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
        }
        
        #accumulate response_size to total, quit crawling timeline texts once
        #no more response or number of docs exceeds threshold value
        r = self.session.post(post_url, data=data, headers=header)
        response_size = r.json()["msg"][0]
        total = total + response_size
        response_html = r.json()["msg"][1]
        for text in BeautifulSoup(response_html).findAll('textarea', class_="content"):
            timelines.append(re.sub('<[^>]+>', '', text.string)) #filter <garbage>
        
        while total < TOP and response_size > 0:
            data_times = re.findall(r"data-time=\"\d+\"", response_html)
            if len(data_times) > response_size:
                return timelines
            latest_data_time = re.search(r"\d+", data_times[response_size - 1]).group()
            data = {
                'start': latest_data_time,
                '_xsrf': _xsrf,
            }
            r = self.session.post(post_url, data=data, headers=header)
            response_size = r.json()["msg"][0]
            total = total + response_size
            response_html = r.json()["msg"][1]
            for text in BeautifulSoup(response_html).findAll('textarea', class_="content"):
                timelines.append(re.sub('<[^>]+>', '', text.string)) #filter <garbage>
        
        return timelines