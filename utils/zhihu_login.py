# -*- coding: utf-8 -*-
'''
Required
- requests
- pillow
'''
import requests
import cookielib
import re
import time
import os.path
from PIL import Image
import random

main_dir = os.path.realpath('..')

#Request headers
#agent = 'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0'
agents = []
with open(main_dir + '/user-agents.txt') as f:
    for l in f:
        agents.append(l.strip())
agent = random.choice(agents)
headers = {
    'User-Agent': agent
}

#use cookie to login
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename= main_dir + '/cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print "Cookie not loaded"


def get_xsrf():
    '''_xsrf is a dynamic parameter'''
    index_url = 'http://www.zhihu.com'
    # get _xsrf for login
    index_page = session.get(index_url, headers=headers)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    # _xsrf is a list
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]


# get verification code
def get_captcha():
    t = str(int(time.time()*1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    #pillow.Image will show up verification image
    im = Image.open('captcha.jpg')
    im.show()
    im.close()

    captcha = input("please input the captcha\n>")
    return captcha

def isLogin():
    #identify login by checking personel page
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url,allow_redirects=False).status_code
    if int(x=login_code) == 200:
        return True
    else:
        return False

def login(secret, account):
    # identify if it is cellphone or email login
    if re.match(r"^1\d{10}$", account):
        print "cell phone number login \n"
        post_url = 'http://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'phone_num': account,
        }
    else:
        print "email login \n"
        post_url = 'http://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'email': account,
        }
    try:
        #no verification code
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = login_page.text
        print login_page.status
        print login_code
    except:
        #require verification code
        postdata["captcha"] = get_captcha()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = eval(login_page.text)
        print login_code['msg']
    
    #save cookies for future use
    session.cookies.save()

def get_session(p_c = 10, p_m = 10, m_r = 100, p_b = False):
    adapter = requests.adapters.HTTPAdapter(pool_connections=p_c, \
        pool_maxsize=p_m, max_retries=m_r, pool_block = p_b)
    session.mount('https://', adapter)
    return session

def get_agents():
    return agents

try:
    input = raw_input
except:
    pass


if __name__ == '__main__':
    if isLogin():
        print 'login successful'
    else:
        account = input("username email\n>  ")
        secret = input("password\n>  ")
        login(secret, account)