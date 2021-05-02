import requests
import json
import config

# cookie = config.bili_cookie

rwd_url = 'http://www.bilibili.com/plus/account/exp.php'
nav_url = 'https://api.bilibili.com/x/web-interface/nav'

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding' : 'gzip',
    'Accept-Language' : 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
}

def getRwdedCoin(cookie):
    r = requests.get(rwd_url, headers=headers, cookies=cookie)
    rwd = json.loads(r.text)
    return rwd['number']

def getNav(cookie):
    r = requests.get(nav_url, headers=headers, cookies=cookie)
    nav = json.loads(r.text)
    return nav

def getAccountInfo(cookie):
    cookie = requests.cookies.cookiejar_from_dict(cookie)
    nav = getNav(cookie)
    rwdcoin = getRwdedCoin(cookie) // 10
    account = {
        'money': nav['data']['money'],
        'cur_level': nav['data']['level_info']['current_level'],
        'cur_exp': nav['data']['level_info']['current_exp'],
        'rwd_coin': rwdcoin,
        'add_need': 5 - rwdcoin,
        'uname': nav['data']['uname'],
    }
    account['time_need'] = 0 if account['cur_level'] == 6 else (28800 - account['cur_exp']) // 50
    return account

# print(getAccountInfo())