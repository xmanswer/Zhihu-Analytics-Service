# -*- coding: utf-8 -*-
"""
Created on Thu May 05 15:30:48 2016

@author: minxu
"""

import urllib2
import re
import threading
import time
rawProxyList = []
checkedProxyList = []
#抓取代理网站
targets = []
for i in xrange(1,10):
        target = r"http://www.proxy.com.ru/list_%d.html" % i
        targets.append(target)
        
#抓取代理服务器正则
p = re.compile(r'''<tr><b><td>(\d+)</td><td>(.+?)</td><td>(\d+)</td><td>(.+?)</td><td>(.+?)</td></b></tr>''')

#获取代理的类
class ProxyGet(threading.Thread):
    def __init__(self,target):
        threading.Thread.__init__(self)
        self.target = target
    def getProxy(self):
        print "target proxy website： " + self.target
        req = urllib2.urlopen(self.target)
        result = req.read()
        #print chardet.detect(result)
        matchs = p.findall(result)
#       print matchs
        for row in matchs:
            ip=row[1]
            port =row[2]
            addr = row[4].decode("cp936").encode("utf-8")
            proxy = [ip,port,addr]
            print proxy
            rawProxyList.append(proxy)
    def run(self):
        self.getProxy()
        
#检验代理的类
class ProxyCheck(threading.Thread):
    def __init__(self,proxyList):
        threading.Thread.__init__(self)
        self.proxyList = proxyList
        self.timeout = 10
        self.testUrl = "https://www.zhihu.com/"
        self.testStr = "11010802010035"
    def checkProxy(self):
        cookies = urllib2.HTTPCookieProcessor()
        for proxy in self.proxyList:
            proxyHandler = urllib2.ProxyHandler({"https" : r'http://%s:%s' %(proxy[0],proxy[1])})
            #print r'http://%s:%s' %(proxy[0],proxy[1])
            opener = urllib2.build_opener(cookies,proxyHandler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')]
            #urllib2.install_opener(opener)
            t1 = time.time()
            try:
                #req = urllib2.urlopen("http://www.baidu.com", timeout=self.timeout)
                req = opener.open(self.testUrl, timeout=self.timeout)
                #print "urlopen is ok...."
                result = req.read()
                #print "read html...."
                timeused = time.time() - t1
                pos = result.find(self.testStr)
                #print "pos is %s" %pos
                if pos > 1:
                    checkedProxyList.append((proxy[0],proxy[1],proxy[2],timeused))
                    #print "ok ip: %s %s %s %s" %(proxy[0],proxy[1],proxy[2],timeused)
                else:
                     continue
            except Exception,e:
                #print e.message
                continue
    def run(self):
        self.checkProxy()    
        
def get_proxies():
    getThreads = []
    checkThreads = []
    #对每个目标网站开启一个线程负责抓取代理
    for i in range(len(targets)):
        t = ProxyGet(targets[i])
        getThreads.append(t)
    for i in range(len(getThreads)):
        getThreads[i].start()
    for i in range(len(getThreads)):
        getThreads[i].join()
    print '.'*10+"crawled %s proxies" %len(rawProxyList) +'.'*10

    #开启20个线程负责校验，将抓取到的代理分成20份，每个线程校验一份
    for i in range(20):
        t = ProxyCheck(rawProxyList[((len(rawProxyList)+19)/20) * i:((len(rawProxyList)+19)/20) * (i+1)])
        checkThreads.append(t)
    for i in range(len(checkThreads)):
        checkThreads[i].start()
    for i in range(len(checkThreads)):
        checkThreads[i].join()
    print '.'*10+"%s prxoies are ready to use" %len(checkedProxyList) +'.'*10
    plist = []
    for p in checkedProxyList:
        plist.append('http://' + p[0] + ':' + p[1])
    if len(plist) == 0:
        plist = None
    return plist