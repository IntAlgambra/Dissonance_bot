# Token 695230871:AAEllCSIVMCT8kwYC0LPxRdsEm80Pe7qvRY

import telebot

token = '695230871:AAEllCSIVMCT8kwYC0LPxRdsEm80Pe7qvRY'

proxies = {'https': 'https://97.80.39.42:45102'}

BASE_URL = 'https://api.telegram.org/bot{}/'.format(token)

r = requests.get(f'{BASE_URL}getMe')

print(r)

print(r.json())
