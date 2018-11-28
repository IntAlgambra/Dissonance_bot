from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, Boolean, ForeignKey, create_engine, update, and_
from sqlalchemy.orm import sessionmaker, relationship

from sqlalchemy.ext.declarative import declarative_base

import random

import json

#Создаем базу данных

SongsDatabase = declarative_base()


#Таблица, в которой сохранены данные о жанрах
class Genre(SongsDatabase):
    __tablename__ = 'genres'

    genre_id = Column(Integer(), primary_key = True, autoincrement = True)
    genre = Column(Unicode())

    #songs = relationship('Song', backref = 'genres')

    check_1 = UniqueConstraint('genre_id')
    check_2 = UniqueConstraint('genre')

#Таблица, в которой сохранены данные о песнях
class Song(SongsDatabase):

    __tablename__ = 'songs'

    song_id = Column(Integer(), primary_key = True, autoincrement = True)
    song_genre_id = Column(Integer(), ForeignKey('genres.genre_id'))
    song_link = Column(Unicode())

    #Checkings
    check_1 = UniqueConstraint('song_id')
    check_2 = UniqueConstraint('song_link')

    def __repr__(self):
        return('link: {0}, genre_id: {1},'.format(self.song_link, self.song_genre_id))

#Таблица, в которой сохранены данные о пользователях бота
class User(SongsDatabase):

    __tablename__ = 'users'
    
    #ID пользователя в базе данных
    user_id = Column(Integer(), primary_key = True, autoincrement = True)
    #ID пользователя в телеграме
    telegram_id = Column(Integer())
    #Словарь песен, уже отправленных пользователю в строке JSON
    listened_songs = Column(Unicode())

    check_1 = UniqueConstraint('user_id')
    check_2 = UniqueConstraint('telegram_id')


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

def add_genre(genre, session):
    genre = Genre(genre = genre)
    session.add(genre)
    session.commit()

def add_song(genre_id, link, session):
    song = Song(song_genre_id = genre_id, song_link = link)
    session.add(song)
    session.commit()

def get_songs_list(session):
    song_query = session.query(Song)
    for song in song_query:
        print(song)

def get_genres(session):
    genres = session.query(Genre.genre).all()
    return(genres)

#Функция для тестового заполнения БД всякой фигней

def random_fill(session, engine):
    SongsDatabase.metadata.drop_all(engine)
    SongsDatabase.metadata.create_all(engine)
    for genre_name in test_genres:
        genre = Genre(genre = genre_name)
        session.add(genre)
        for i in range(100):
            link = genre_name + '_{}'.format(i)
            song = Song(song_genre = genre_name, song_link = link)
            session.add()
    session.commit()