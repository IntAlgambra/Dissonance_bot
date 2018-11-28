from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship

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

class User(DB):

	__tablename__ = 'users'

	uid = Column(Integer, primary_key = True, unique = True)

class Listened(DB):

	__tablename__ = 'listened'

	__table_args__ = (UniqueConstraint('song', 'user_id', name = 'uix_1'), )

	lid = Column(Integer, primary_key = True, autoincrement = True)
	song = Column(String, ForeignKey('songs.link', onupdate = "CASCADE", ondelete = "CASCADE"))
	user_id = Column(Integer, ForeignKey('users.uid', onupdate = "CASCADE", ondelete = "CASCADE"))

#Класс для работы с БД

class Database():

	def __init__(self, filename = 'dbt'):
		self.database = DB
		self.filename = filename
		self.engine = create_engine('sqlite:///{}.db'.format(self.filename))
		self.session = sessionmaker(bind = self.engine)()

	def create_all(self):
		self.database.metadata.create_all(self.engine)

	def update_all(self):
		self.database.metadata.drop_all(self.engine)
		self.database.metadata.create_all(self.engine)

	def add_genre(self, genre):
		try:
		    genre = Genre(genre = genre)
		    self.session.add(genre)
		    self.session.commit()
		except IntegrityError:
			self.session.rollback()
			print('This genre is already in database')

	def delete_genre(self, genre):
		try:
		    genre = self.session.query(Genre).filter(Genre.genre == genre).first()
		    self.session.delete(genre)
		    self.session.commit()
		except UnmappedInstanceError:
			self.session.rollback()
			print('There is no such genre')

	def add_song(self, link, genre):
		try:
		    song = Song(link = link, genre = genre)
		    self.session.add(song)
		    self.session.commit()
		except IntegrityError:
			self.session.rollback()
			print('This song is already in database')

	def delete_song(self, link):
		try:
		    song = self.session.query(Song).filter(Song.link == link).first()
		    self.session.delete(song)
		    self.session.commit()
		except UnmappedInstanceError:
			self.session.rollback()
			print('There is no such song')
		pass

	def add_user(self, user_id):
		try:
		    user = User(uid = user_id)
		    self.session.add(user)
		    self.session.commit()
		except IntegrityError:
			self.session.rollback()
			print('This user is already in database')

	def delete_user(self, user_id):
		try:
		    user = self.session.query(User).filter(User.uid == user_id).first()
		    self.session.delete(user)
		    self.session.commit()
		except UnmappedInstanceError:
			self.session.rollback()
			print('There is no such user')

	def add_listened(self, user_id, song):
		listened_song = Listened(song = song, user_id = user_id)
		self.session.add(listened_song)
		self.session.commit()

	def get_random_from_genre(self, genre, user_id):
		#Генерируем начальное значение для генератора случайных чисел
		random.seed()
		#Формируем список уже отправленных пользователю песен
		listened_query = self.session.query(Listened).filter(Listened.user_id == user_id).all()
		listened_songs = [item.song for item in listened_query]
		#Формируем список песен, еще не отправленных пользователю и выбираем из списка рандомную
		songs_from_genre = self.session.query(Song).filter(Song.genre == genre).filter(~Song.link.in_(listened_songs)).all()
		random_song = random.choice(songs_from_genre)
		random_song_link = random_song.link
		return random_song_link

	def get_genres(self):
		genres_query = self.session.query(Genre).all()
		genres = [genre.genre for genre in genres_query]
		return genres

	def add_test_data(self):
		self.update_all()
		for genre in ['folk', 'rock', 'techno']:
			self.add_genre(genre)
			for i in range(10):
				link = '{0}_{1}'.format(genre, i)
				self.add_song(link, genre)
		for i in range(10):
			self.add_user(i)