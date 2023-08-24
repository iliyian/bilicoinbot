from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

import requests
import random

import config
import qrlogin
import account
import json
import atexit
import video

token = config.tgbot_token

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

@atexit.register
def save():
    with open('user_state.json', 'wb') as f:
        f.write(json.dumps(user_state, sort_keys=True, indent=4).encode())

user_state = {}
with open('user_state.json', 'rb') as f:
    user_state = json.loads(f.read(-1))


def start_command(update: Update, _: CallbackContext):
    update.message.reply_text('为了获取最多的经验值》《，为了尽快升上六级，此bot助你一臂之力，衝鸭！！')

def help_command(update: Update, _: CallbackContext):
    update.message.reply_text('\
        这是一个自己研发的机器人，托管在github[https://github.com/iliyian/bilicoinbot]上，求赏个star吧QAQ\n\
        总之我只是一只可爱的小猫咪~我什么都不知道~\
    ')


def login_command(update: Update, _: CallbackContext):
    username = update.message.from_user.username
    # if username not in user_state: or not user_state[username]['logged']:
    key = qrlogin.makeQR(username)
    user_state[username] = {
        'oauthKey': key,
        'scanning': True,
        'logged': False,
    }
    with open('qrs/%s.jpg' % username, 'rb') as f:
        update.message.reply_photo(
            caption='鳉鳉鳉！开始使用前亲先请扫码登录哦~~~ 然后用 /verify 验证是否成功\n（这个作者太懒搞不懂人机验证',
            photo=f
        )
    # else:
    #     update.message.reply_text('你已经上船啦~~所以不可以再登一次哦~=_=')
    save()

def verify_command(update: Update, _: CallbackContext):
    username = update.message.from_user.username
    if username in user_state and user_state[username]['scanning']:
        data = {
            'oauthKey': user_state[username]['oauthKey'],
            'gourl': 'https://www.bilibili.com'
        }
        r = requests.post(qrlogin.qrinfourl, data=data, headers=account.headers)
        jr = json.loads(r.text)
        if jr['status']:
            # print(r.headers)
            user_state[username]['cookie'] = dict(r.cookies)
            # update.message.reply_text(r.headers['Set-Cookie'])
            update.message.reply_text('确认扫码成功！接下来可以用 /account 查看账户信息和用 /coin 自动投币啦')
            user_state[username]['scanning'] = False
            user_state[username]['logged'] = True
        else:
            update.message.reply_text(jr['message'])

    elif username in user_state and user_state[username]['logged']:
        update.message.reply_text('你已经上船啦~~所以可以开始投币了哦 用 /account 或 /coin 试试康')
    else:
        update.message.reply_text('请先扫描二维码哦~~')
    save()

def account_command(update: Update, _: CallbackContext):
    username = update.message.from_user.username
    if username in user_state and user_state[username]['logged']:
        username = update.message.from_user.username
        info = account.getAccountInfo(user_state[username]['cookie'])
        update.message.reply_text(
            '%s 你好呀~!（握爪，你的账户信息如下：\n当前等级：Lv%d\n当前经验值：%d\n剩余硬币：%d\n当天已使用硬币获得之经验数：%d\n距离Lv6还剩%d天'
            % (info['uname'], info['cur_level'], info['cur_exp'], info['money'], info['rwd_coin'] * 10, info['time_need'])
        )
    else:
        update.message.reply_text('请小海盗先上船吧~~')


coin_url = 'http://api.bilibili.com/x/web-interface/coin/add'

def add(aid, username):
    if username in user_state and user_state[username]['logged']:
        data = {
            'aid': aid,
            'multiply': 1,
            'select_like': 1,
            'csrf': user_state[username]['cookie']['bili_jct']
        }
        cookie = requests.cookies.cookiejar_from_dict(user_state[username]['cookie'])
        r = requests.post(coin_url, data=data, cookies=cookie)
        return r.json()['message']


def coin_command(update: Update, _: CallbackContext):
    username = update.message.from_user.username
    if username in user_state and user_state[username]['logged']:
        select_videos = random.sample(video.getTop100Videos(), 5)
        message = '开始投币啦！\n'
        for i in range(0, 5):
            m = add(select_videos[i]['aid'], username)
            message += '[' + str(i) + ']：' + select_videos[i]['title']
            if m == '0':
                message += ' 投币成功！\n'
            else:
                message += m + '\n'
        update.message.reply_text(message)
    else:
        update.message.reply_text('哎呀呀，请一步一步来首先登录哦')

def message(update: Update, _: CallbackContext):
    update.message.reply_text(update.message.text)

def bot():
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('login', login_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('verify', verify_command))
    dispatcher.add_handler(CommandHandler('account', account_command))
    dispatcher.add_handler(CommandHandler('coin', coin_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message))
    updater.start_polling()
    updater.idle()

bot()
