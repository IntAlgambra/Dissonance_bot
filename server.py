from flask import Flask
from flask import request

from flask_sslify import SSLify

import time

import telebot

from bot import bot
from admin_bot import bot as admin_bot

#Базовый url веб приложения, на котором крутится сервер с ботом при запуске на локальном компьютере через ngrok
#WEBHOOK_BASE = 'YOUR URL'
#Базовый url при запуске на сервере (раскомментировать при запуске на сервере)
WEBHOOK_BASE = 'YOUR WEB APP URL'
BOT_URL = '/bot'
ADMIN_BOT_URL = '/admin_bot'
#url для webhook рабочего бота
BOT_WEBHOOK = WEBHOOK_BASE + BOT_URL
#url для webhook админского бота
ADMIN_BOT_WEBHOOK = WEBHOOK_BASE + ADMIN_BOT_URL

app = Flask(__name__)
sslify = SSLify(app)

#Главная страница, которая нафиг не нужна
@app.route('/')
def index():
    return('This is sochnye bitochky bots app')

#Обработчки запросов от телеги к рабочему боту
@app.route('/bot', methods = ['POST', 'GET'])
def bot_app():
    if request.method == 'POST':
        update_json = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(update_json)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        return('This is sochnye bitochky bot app')

#Обработчик запросов от телеги к админскому боту
@app.route('/admin_bot', methods = ['POST', 'GET'])
def admin_bot_app():
    if request.method == 'POST':
        update_json = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(update_json)
        admin_bot.process_new_updates([update])
        return 'ok', 200
    else:
        return('This is sochnye bitochky admin bot app')

#на всякий случай сбрасываем вебхук (если, например, сменили адрес)
bot.remove_webhook()
admin_bot.remove_webhook()

time.sleep(0.1)

#Устанавливаем вебхуки на ботов
bot.set_webhook(url = BOT_WEBHOOK)
admin_bot.set_webhook(url = ADMIN_BOT_WEBHOOK)

if __name__ == '__main__':
    app.run()