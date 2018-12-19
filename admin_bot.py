# Token 703792165:AAHXhlm08UQ05UjqkrjxAEYYJfTA2Lxmubo

from dbt import Database

import requests

import telebot
from telebot import apihelper
from telebot import types


TOKEN = '703792165:AAHXhlm08UQ05UjqkrjxAEYYJfTA2Lxmubo'

#Прокси для тестирования бота на локальном компе через тор, при развертывании на сервере закомментировать
apihelper.proxy = {'https': 'socks5://127.0.0.1:9150'}

#Создаем объект для доступа к базе данных
db = Database('database')

#Создаем объект клавиатуры для добавления песни
def make_add_song_keyboard():
    genres = db.get_genres()
    add_song_keyboard = types.InlineKeyboardMarkup(row_width = 1)
    for genre in genres:
        button = types.InlineKeyboardButton(text = genre, callback_data = 'add_{}'.format(genre))
        add_song_keyboard.add(button)
    cancel_button = types.InlineKeyboardButton(text = 'cancel', callback_data = 'add_cancel')
    add_song_keyboard.add(cancel_button)
    return(add_song_keyboard)

#Создаем объект клавиатуры для удаления жанра
def make_del_genre_keyboard():
    genres = db.get_genres()
    del_genre_keyboard = types.InlineKeyboardMarkup(row_width = 1)
    for genre in genres:
        button = types.InlineKeyboardButton(text = genre, callback_data = 'del_{}'.format(genre))
        del_genre_keyboard.add(button)
    cancel_button = types.InlineKeyboardButton(text = 'cancel', callback_data = 'del_cancel')
    del_genre_keyboard.add(cancel_button)
    return(del_genre_keyboard)

#Создаем функцию для проверки валидности ссылки на песню на SoundCloud
def validate_link(link):
    try:
        r = requests.get(link)
        if r.status_code == requests.codes.ok:
            return True
        else:
            return False
    except requests.exceptions.MissingSchema as e:
        return False

#создаем объект бота, запрещаем многопоточность по требованиям хостинга
bot = telebot.TeleBot(TOKEN, threaded = False)

#Обработчик команды старт
@bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = message.from_user
    user_id = user.id
    bot.reply_to(message, 'Welcome, master of techno and style!')

#Получение списка жанров
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

#Блок добавления нового жанра (в который можно будет добавлять песни)
@bot.message_handler(commands = ['add_genre'])
def add_genre(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'input genre_name or N/n to cancel')
    bot.register_next_step_handler(msg, genre_handler)

def genre_handler(message):
    try:
        chat_id = message.chat.id
        genre = message.text
        if genre == 'N' or genre == 'n':
            bot.send_message(chat_id, 'canceled')
        else:
            db.add_genre(genre)
            bot.send_message(chat_id, 'Added')
    except Exception as e:
        bot.reply_to(message, 'some problem occured, genre has not been added')

#Блок добавления новой песни в два шага: 1 - выбор жанра, 2 - ввод ссылки
@bot.message_handler(commands = ['add_song'])
def add_song(message):
    chat_id = message.chat.id
    add_song_keyboard = make_add_song_keyboard()
    bot.send_message(chat_id, 'choose genre', reply_markup = add_song_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'add')
def add_genre_choice(call):
    if call.message:
        if call.data:
            genre = call.data.split('_')[-1]
            chat_id = call.message.chat.id
            if genre == 'cancel':
                bot.send_message(chat_id, 'canceled')
            else:
                msg = bot.send_message(chat_id, 'input link to SoundCloud')
                bot.register_next_step_handler(msg, link_handler, genre)

def link_handler(message, genre):
    try:
        chat_id = message.chat.id
        link = message.text
        if validate_link(link):
            db.add_song(link, genre)
            bot.send_message(chat_id, 'added')
        else:
            bot.reply_to(message, 'This link is not valid')
    except Exception as e:
        bot.reply_to(message, 'some problem occured, song has not been added')

#Блок удаления жанра (жанр удаляется вместе со всеми песнями)
@bot.message_handler(commands = ['del_genre'])
def del_genre(message):
    chat_id = message.chat.id
    del_genre_keyboard = make_del_genre_keyboard()
    bot.send_message(chat_id, 'choose genre', reply_markup = del_genre_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'del')
def del_genre_choice(call):
    if call.message:
        if call.data:
            genre = call.data.split('_')[-1]
            chat_id = call.message.chat.id
            if genre == 'cancel':
                bot.send_message(chat_id, 'canceled')
            else:
                result = db.delete_genre(genre)
                if result:
                    bot.send_message(chat_id, 'success')
                else:
                    bot.send_message(chat_id, 'fail to delete genre')

#Блок удаления песни
@bot.message_handler(commands = ['del_song'])
def del_song(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'input link to song you want to delete or N/n to cancel')
    bot.register_next_step_handler(msg, del_song_handler)

def del_song_handler(message):
    link = message.text
    chat_id = message.chat.id
    if link == 'N' or link == 'n':
        bot.send_message(chat_id, 'canceled')
    else:
        result = db.delete_song(link)
        if result:
            bot.send_message(chat_id, 'success')
        else:
            bot.send_message(chat_id, 'fail')

if __name__ == '__main__':
    bot.polling()