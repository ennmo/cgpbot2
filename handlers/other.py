import requests
import time
from create import tg_token


def send_action(chat_id):
    while True:
        requests.get(f'https://api.telegram.org/bot{tg_token}/sendChatAction',
                     params={'chat_id': chat_id, 'action': 'typing'})
        time.sleep(5)
