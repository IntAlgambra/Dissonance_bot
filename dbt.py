from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm.exc import UnmappedInstanceError

from sqlalchemy.engine import Engine

from sqlalchemy import event

import random

#Обработчик для автоматического включения внешних ключей в sqlite3
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

#Создаем базу данных

DB = declarative_base()


#Таблица, в которой сохранены данные о жанрах
class Genre(DB):
    __tablename__ = 'genres'

    gid = Column(Integer, primary_key = True, autoincrement = True)
    genre = Column(String, unique = True)

#Таблица, в которой сохранены данные о песнях
class Song(DB):

    __tablename__ = 'songs'

    sid = Column(Integer, primary_key = True, autoincrement = True)
    genre = Column(String, ForeignKey('genres.genre', onupdate = "CASCADE", ondelete = "CASCADE"))
    link = Column(String, unique = True)

    def __repr__(self):
        return('link: {0}, genre: {1},'.format(self.link, self.genre))

class Chat(DB):

	__tablename__ = 'chats'

	chid = Column(Integer, primary_key = True, unique = True)

class Listened(DB):

	__tablename__ = 'listened'

	__table_args__ = (UniqueConstraint('song', 'chat_id', name = 'uix_1'), )

	lid = Column(Integer, primary_key = True, autoincrement = True)
	song = Column(String, ForeignKey('songs.link', onupdate = "CASCADE", ondelete = "CASCADE"))
	chat_id = Column(Integer, ForeignKey('chats.chid', onupdate = "CASCADE", ondelete = "CASCADE"))

#Класс для работы с БД

class Database():

	def __init__(self, filename = 'dbt'):
		self.database = DB
		self.filename = filename
		self.engine = create_engine('sqlite:///{}.db'.format(self.filename))
		self.session_factory = sessionmaker(bind = self.engine)
		self.session = scoped_session(self.session_factory)

	def create_all(self):
		self.database.metadata.create_all(self.engine)

	def update_all(self):
		self.database.metadata.drop_all(self.engine)
		self.database.metadata.create_all(self.engine)

	def add_genre(self, genre):
		session = self.session()
		try:
		    genre = Genre(genre = genre)
		    session.add(genre)
		    session.commit()
		except IntegrityError:
			session.rollback()
			print('This genre is already in database')
		finally:
		    self.session.remove()

	def delete_genre(self, genre):
		session = self.session()
		try:
		    genre = session.query(Genre).filter(Genre.genre == genre).first()
		    session.delete(genre)
		    session.commit()
		    return True
		except UnmappedInstanceError:
			session.rollback()
			return False
		finally:
		    self.session.remove()

	def add_song(self, link, genre):
		session = self.session()
		try:
		    song = Song(link = link, genre = genre)
		    session.add(song)
		    session.commit()
		    return True
		except IntegrityError:
			session.rollback()
			return False
		finally:
		    self.session.remove()

	def delete_song(self, link):
		session = self.session()
		try:
		    song = session.query(Song).filter(Song.link == link).first()
		    session.delete(song)
		    session.commit()
		    return(True)
		except UnmappedInstanceError:
			session.rollback()
			return(False)
		finally:
		    self.session.remove()

	def add_chat(self, chat_id):
		session = self.session()
		try:
		    chat = Chat(chid = chat_id)
		    session.add(chat)
		    session.commit()
		    return True
		except IntegrityError:
			session.rollback()
			return False
		finally:
		    self.session.remove()

	def delete_chat(self, chat_id):
		session = self.session()
		try:
		    chat = session.query(Chat).filter(Chat.chid == chat_id).first()
		    session.delete(chat)
		    session.commit()
		    return True
		except UnmappedInstanceError:
			session.rollback()
			return False
		finally:
			self.session.remove()

	def add_listened(self, chat_id, song):
		session = self.session()
		try:
		    listened_song = Listened(song = song, chat_id = chat_id)
		    session.add(listened_song)
		    session.commit()
		    return True
		except Exception as e:
			return False
		finally:
		    self.session.remove()

	def get_random_from_genre(self, genre, chat_id):
		session = self.session()
		#Генерируем начальное значение для генератора случайных чисел
		random.seed()
		#Формируем список уже отправленных пользователю песен
		listened_query = session.query(Listened).filter(Listened.chat_id == chat_id).all()
		listened_songs = [item.song for item in listened_query]
		#Формируем список песен, еще не отправленных пользователю и выбираем из списка рандомную
		songs_from_genre = session.query(Song).filter(Song.genre == genre).filter(~Song.link.in_(listened_songs)).all()
		#Если остались непрослушанные печни (список не пуст, оправляем ссылку)
		if songs_from_genre:
		    random_song = random.choice(songs_from_genre)
		    random_song_link = random_song.link
		    self.session.remove()
		    return random_song_link
		else:
			self.session.remove()
			return None

	def get_genres(self):
		session = self.session()
		genres_query = session.query(Genre).all()
		genres = [genre.genre for genre in genres_query]
		self.session.remove()
		return genres