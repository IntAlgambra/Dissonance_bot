# Token 695230871:AAEllCSIVMCT8kwYC0LPxRdsEm80Pe7qvRY

import requests
import telebot
import pprint

token = '695230871:AAEllCSIVMCT8kwYC0LPxRdsEm80Pe7qvRY'

proxies = {'http': 'socks5://127.0.0.1:9150', 'https': 'socks5://127.0.0.1:9150'}

BASE_URL = 'https://api.telegram.org/bot{}/'.format(token)

r = requests.get(f'{BASE_URL}getMe', proxies = proxies)

print(r)

print(r.json())

r = requests.get(f'{BASE_URL}getUpdates', proxies = proxies)

pprint.pprint(r.json())

try:
    last_update_id = r.json()['result'][-1]['update_id']
    r = requests.get('{0}getUpdates?offset={1}'.format(BASE_URL, last_update_id + 1), proxies = proxies)
    pprint.pprint(r)
    pprint.pprint(r.json())
except:
	pass

