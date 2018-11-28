# Token 703792165:AAHXhlm08UQ05UjqkrjxAEYYJfTA2Lxmubo

from dbt import Database

import requests

import telebot
from telebot import apihelper
from telebot import types

import pprint

TOKEN = '703792165:AAHXhlm08UQ05UjqkrjxAEYYJfTA2Lxmubo'

apihelper.proxy = {'https': 'socks5://127.0.0.1:9150'}

#Создаем объект для доступа к базе данных
db = Database()

#Словарь для записи пар жанр-песня для конкретного чата
song_updater = {}

#Получаем список жанров из базы данных
genres = db.get_genres()

#Создаем объект клавиатуры
genre_keyboard = types.InlineKeyboardMarkup(row_width = 1)
for genre in genres:
    button = types.InlineKeyboardButton(text = genre, callback_data = genre)
    genre_keyboard.add(button)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = message.from_user
    user_id = user.id
    bot.reply_to(message, 'Welcome, master of techno and style!')

@bot.message_handler(commands = ['get_genres'])
def send_genres(message):
    chat_id = message.chat.id
    genres = db.get_genres()
    if genres:
        genres_list = ''
        for genre in genres:
            genres_list += '{}\n'.format(genre)
        bot.send_message(chat_id, genres_list)
    else:
        bot.send_message(chat_id, 'There are no genres yet')

@bot.message_handler(commands = ['add_genre'])
def add_genre(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'input genre_name')
    bot.register_next_step_handler(msg, genre_handler)

def genre_handler(message):
    try:
        chat_id = message.chat.id
        genre = message.text
        db.add_genre(genre)
        bot.send_message(chat_id, 'Added')
    except Exception as e:
        bot.reply_to(message, 'oops')

@bot.message_handler(commands = ['add_song'])
def add_song(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'choose genre', reply_markup = genre_keyboard)

@bot.callback_query_handler(func=lambda call: call.data in genres)
def genre_choice(call):
    if call.message:
        if call.data:
            genre = call.data
            chat_id = call.message.chat.id
            song_updater[chat_id] = genre
            msg = bot.send_message(chat_id, 'input link to SoundCloud')
            bot.register_next_step_handler(msg, link_handler)

def link_handler(message):
    try:
        chat_id = message.chat.id
        link = message.text
        db.add_song(link, song_updater[chat_id])
    except Exception as e:
        bot.reply_to(message, 'ooops')

if __name__ == '__main__':
    bot.polling()