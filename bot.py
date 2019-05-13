#Импортируем модуль для взаимодействия с базой данных
from dbt import Database

#Импортируем библиотеку для работы с API телеграм ботов
import telebot
from telebot import types

TOKEN = 'YOUR TOKEN'

HELLO = 'Привет, я Нина.\n\nЯ здесь для того, чтобы поделиться с тобой музыкой. Какую ты хочешь послушать?'

#Прокси для тестирования бота на локальном компе через тор, при развертывании на сервере закомментировать
#apihelper.proxy = {'https': 'socks5://127.0.0.1:9150'}

#Создаем объект для доступа к базе данных
db = Database('database')

#Создаем объект клавиатуры
def make_genre_keyboard():
    genres = db.get_genres()
    genre_keyboard = types.InlineKeyboardMarkup(row_width = 1)
    for genre in genres:
        button = types.InlineKeyboardButton(text = genre, callback_data = genre)
        genre_keyboard.add(button)
    return(genre_keyboard)

#Функция для создания клавиатуры для прослушивания песни и выбора новой
def make_listen_or_choice_keyboard(url):
    listen_or_choice_keyboard = types.InlineKeyboardMarkup(row_width = 1)
    listen_button = types.InlineKeyboardButton(text = 'Слушать!', url = url)
    new_button = types.InlineKeyboardButton(text = 'Хочу другой', callback_data = 'new_track')
    listen_or_choice_keyboard.add(listen_button, new_button)
    return(listen_or_choice_keyboard)

#Создаем объект бота, запрещаем многопоточность по требованиям хостинга
bot = telebot.TeleBot(TOKEN, threaded = False)

#Обработчик команды start
@bot.message_handler(commands = ['start'])
def send_welcome(message):
    chat_id = message.chat.id
    db.add_chat(chat_id)
    if db.get_genres():
        genre_keyboard = make_genre_keyboard()
        bot.send_message(chat_id, HELLO, reply_markup = genre_keyboard)
    else:
        bot.send_message(chat_id, 'Sorry, there are no genres yet')

#Обработчик удаления истории прослушанных
@bot.message_handler(commands = ['del_me'])
def del_me(message):
    chat_id = message.chat.id
    db.delete_chat(chat_id)
    db.add_chat(chat_id)
    bot.send_message(chat_id, 'ok')

#Обработчик нажатия на кнопку жанра
@bot.callback_query_handler(func=lambda call: call.data in db.get_genres())
def genre_choice(call):
    if call.message:
        if call.data:
            genre = call.data
            chat_id = call.message.chat.id
            link = db.get_random_from_genre(genre, chat_id)
            if link:
                listen_or_choice_keyboard = make_listen_or_choice_keyboard(link)
                bot.send_message(chat_id, 'Держи \n {}'.format(link), reply_markup = listen_or_choice_keyboard)
                db.add_listened(chat_id, link)
            else:
                genre_keyboard = make_genre_keyboard()
                bot.send_message(chat_id, 'Вы все послушали. Может быть, другой жанр?', reply_markup = genre_keyboard)
            bot.answer_callback_query(call.id, text = '')

#Обработчик нажатия на кнопку запроса нового трека
@bot.callback_query_handler(func = lambda call: call.data == 'new_track')
def new_genre_choice(call):
    chat_id = call.message.chat.id
    if db.get_genres():
        genre_keyboard = make_genre_keyboard()
        bot.send_message(chat_id, 'Выбери еще', reply_markup = genre_keyboard)
    else:
        bot.send_message(chat_id, 'Sorry, there are no genres yet')
    bot.answer_callback_query(call.id, text = '')

if __name__ == '__main__':
    bot.polling()