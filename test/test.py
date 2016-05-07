# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 11:32:25 2016

@author: minxu
"""

# encoding=utf-8
import jieba

seg_list = jieba.cut("第一类是基于字符串匹配，即扫描字符串，如果发现字符串的子串和词相同，就算匹配", cut_all=True)
print "Full Mode: " + "/ ".join(seg_list)  # 全模式

seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
print "Default Mode: " + "/ ".join(seg_list)  # 精确模式

seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
print ", ".join(seg_list)

seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")  # 搜索引擎模式
print ", ".join(seg_list)