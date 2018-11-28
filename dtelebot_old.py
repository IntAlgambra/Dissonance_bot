# Token 695230871:AAEllCSIVMCT8kwYC0LPxRdsEm80Pe7qvRY

from dbt import Database

import requests

import telebot
from telebot import apihelper
from telebot import types

import pprint

import copy

TOKEN = '695230871:AAEllCSIVMCT8kwYC0LPxRdsEm80Pe7qvRY'

apihelper.proxy = {'https': 'socks5://127.0.0.1:9150'}

#Создаем объект для доступа к базе данных

db = Database('test_database')

#Создаем разметку клавиатуры для выбора одного жанра

#Получаем список жанров из базы данных
genres = db.get_genres()

#Создаем объект клавиатуры
keyboard = types.InlineKeyboardMarkup(row_width = 1)
for genre in genres:
    button = types.InlineKeyboardButton(text = genre, callback_data = genre)
    keyboard.add(button)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = message.from_user
    user_id = user.id
    db.add_user(user_id)
    bot.reply_to(message, 'Pssss, man, do you want some music?', reply_markup = keyboard)

@bot.callback_query_handler(func=lambda call: True)
def bot_main(call):
    if call.message:
        if call.data:
            genre = call.data
            user_id = call.message.from_user.id
            link = db.get_random_from_genre(genre, user_id)
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            if link:
                url_button = types.InlineKeyboardButton(text = 'Liten track!', url = link)
                new_keyboard = copy.deepcopy(keyboard)
                new_keyboard.add(url_button)
                bot.edit_message_reply_markup(chat_id, message_id, reply_markup = new_keyboard)
            else:
                bot.send_message(chat_id, 'you have listened all')

                
if __name__ == '__main__':
    bot.polling()





