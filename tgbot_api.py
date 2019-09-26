import requests as req
import os

url = os.environ['BOT_URL']
timeout = 30


def get_updates(offset: int):
    return req.get(url + 'getUpdates', data={'offset': offset, 'timeout': timeout}).json()


def send_message(chat_id, text, reply_markup=''):
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup != '':
        data.update({'reply_markup': reply_markup})
    return req.post(url + 'sendMessage', data).json()


def delete_message(chat_id, message_id):
    return req.post(url + 'deleteMessage', data={'chat_id': chat_id, 'message_id': message_id}).json()
