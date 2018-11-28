from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, Boolean, ForeignKey, create_engine, update, and_
from sqlalchemy.orm import sessionmaker, relationship

from sqlalchemy.ext.declarative import declarative_base

import random

import json

#Создаем базу данных

SongsDatabase = declarative_base()

#Список жанров
genres = ['Кисло', 'Модно', 'Танцевально', 'Хорошие песенки', 'Глубокое, въебывающее техно']

#Шаблон для словаря, содержащего уже скинутые пользователю песни
listened = {item: [] for item in genres}

#Создаем исключений, которое возбуждается при потыке добавить песню в жанр, отсутствующий в списке

class WrongGenre(Exception):
    pass

#Таблица, в которой сохранены данные о жанрах
class Genre(SongsDatabase):
    __tablename__ = 'genres'

    genre_id = Column(Integer(), primary_key = True, autoincrement = True)
    genre = Column(Unicode())

    check_1 = UniqueConstraint(genre_id)
    check_2 = UniqueConstraint(genre)

#Таблица, в которой сохранены данные о песнях
class Song(SongsDatabase):

    __tablename__ = 'songs'

    song_id = Column(Integer(), primary_key = True, autoincrement = True)
    song_genre = Column(Unicode(), ForeignKey(genres.genre))
    song_link = Column(Unicode())
    #Порядковый номер песни в жанре, используется для рандомного выбора
    song_number_in_genre = Column(Integer())

    #Checkings
    check_1 = UniqueConstraint('song_id')
    check_2 = UniqueConstraint('song_link')

    def __repr__(self):
        return('link: {0}, genre: {1}, numer_in_genre: {2}'.format(self.song_link, self.song_genre, self.song_number_in_genre))

#Таблица, в которой сохранены данные о пользователях бота
class User(SongsDatabase):

    __tablename__ = 'users'

    user_id = Column(Integer(), primary_key = True, autoincrement = True)
    #ID пользователя в телеграме
    telegram_id = Column(Integer())
    #Словарь песен, уже отправленных пользователю в строке JSON
    listened_songs = Column(Unicode())

    check_1 = UniqueConstraint('user_id')
    check_2 = UniqueConstraint(telegram_id)


#Функции для работы с базой данных

def connect_to_database(filename = 'test_songs'):
    engine = create_engine('sqlite:///{}.db'.format(filename))
    session = sessionmaker(bind = engine)()
    return(session, engine)


def dump_database(engine):
    answer = input('This action will wipe out all data. Are you sure? Press "Y" to continue')
    if answer == "y" or answer == "Y":
        SongsDatabase.metadata.drop_all(engine)
        SongsDatabase.metadata.create_all(engine)

def add_genre(genre):
    genres.append(genre)

def add_song(genre, link, session):
    number_of_songs = session.query(Song).filter(Song.song_genre == genre).count()
    new_song_number_in_genre = number_of_songs + 1
    try:
        song = Song(song_genre = genre, song_link = link, song_number_in_genre = new_song_number_in_genre)
        if genre not in genres:
            raise WrongGenre(Exception)
    except WrongGenre:
        return('There is no such genre')
    else:
        session.add(song)
        session.commit()
        return('Ok')

def get_songs_list(session):
    song_query = session.query(Song)
    for song in song_query:
        print(song)

def get_genres(session):
    genres = session.query(Genre.genre).all()
    return(genres)

def get_random_song_from_genre(session, genre):
    random.seed()
    number_of_songs = session.query(Song).filter(Song.song_genre == genre).count()
    number = random.randint(1, number_of_songs)
    random_song = session.query(Song).filter(and_(Song.song_genre == genre, Song.song_number_in_genre == number)).first()
    #print(random_song.song_link)
    random.seed()
    return(random_song.song_link)

def get_song(genre, listened):
    filename = 'test_songs'
    engine = create_engine('sqlite:///{}.db'.format(filename))
    session = sessionmaker(bind = engine)()
    random.seed()
    number_of_songs = session.query(Song).filter(Song.song_genre == genre).count()
    number = random.randint(1, number_of_songs)
    random_song = session.query(Song).filter(and_(Song.song_genre == genre, Song.song_number_in_genre == number)).first()
    #print(random_song.song_link)
    random.seed()
    return(random_song.song_link)

def add_user(telegram_id):
    filename = 'test_songs'
    engine = create_engine('sqlite:///{}.db'.format(filename))
    session = sessionmaker(bind = engine)()
    listened_json = json.dumps(listened)
    user = User(telegram_id = telegram_id, listened_songs = listened_json)
    session.add(user)
    session.commit()

def add_song_to_listened(telegram_id, link, genre):
    filename = 'test_songs'
    engine = create_engine('sqlite:///{}.db'.format(filename))
    session = sessionmaker(bind = engine)()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    listened_songs = user.listened_songs
    listened_from_genre = json.loads(listened_songs)
    listened_from_genre[genre].append(link)
    new_listened_songs = json.dumps(listened_from_genre)
    user.listened_songs = new_listened_songs
    session.commit()

def get_listened_from_genre(telegram_id, genre):
    filename = 'test_songs'
    engine = create_engine('sqlite:///{}.db'.format(filename))
    session = sessionmaker(bind = engine)()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    listened_songs = user.listened_songs
    listened_from_genre = json.loads(listened_songs)[genre]
    return(listened_from_genre)

#Служебная функция для наполнения базы данных чем попало для тестирования

def random_fill(session, engine):
    SongsDatabase.metadata.drop_all(engine)
    SongsDatabase.metadata.create_all(engine)
    for genre in genres:
        for i in range(100):
            link = '{0}_link_{1}'.format(genre, i)
            res = add_song(genre, link, session)
