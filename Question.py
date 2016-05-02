# -*- coding: utf-8 -*-
"""
Created on Mon May 02 16:04:53 2016

@author: minxu
"""

from bs4 import BeautifulSoup
import re
import os
import os.path
import json

zhihu_url = "https://www.zhihu.com"
subdir = '/questions/'

def check_question(qid):
    return os.path.exists(os.getcwd() + subdir + qid)

class Question:
    
    #todo
    def __init__(self, qid):
        self.url = zhihu_url + '/question/' + qid
    
    def evaluate(self):
        return 0
    
    def flush(self):
        return 0
    
    def get_qnum(self):
        return 0
    
    def get_question(self):
        return 0
    
    def get_answers(self):
        return 0