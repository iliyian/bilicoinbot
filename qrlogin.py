import requests
import qrcode
import json

qrurl = 'http://passport.bilibili.com/qrcode/getLoginUrl'
qrinfourl = 'https://passport.bilibili.com/qrcode/getLoginInfo'

def makeQR(tgname):
    r = requests.get(qrurl)
    data = json.loads(r.text)
    img = qrcode.make(data=data['data']['url'])
    key = data['data']['oauthKey']
    with open('qrs/%s.jpg' % tgname, 'wb') as f:
        img.save(f)
    return key

makeQR('iliyian')