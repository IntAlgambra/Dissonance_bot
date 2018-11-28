
import urllib.request

import requests

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import os

from dbt import Database

GENRES_DICT = {'Кисло':'Acid', 'Танцевально':'Dancing', 'Глубокое, въебывающее техно':'Techno', 'Модно': 'Popular'}

DB_FILENAME = 'test_database'

db = Database(DB_FILENAME)


def prepare_database(filename):
    db.update_all()
    for genre in list(GENRES_DICT.keys()):
        db.add_genre(genre)

def get_50_from_genre(page):

    with open(page, encoding = 'utf-8') as f:
        html = f.read()

    #print(html)

    soup = BeautifulSoup(html, 'lxml')

    tracks_div_list = soup.find_all('li', class_ = 'chartTracks__item')

    tracks_a_list = [div.find('a', class_ = 'sc-link-dark') for div in tracks_div_list]
    print(tracks_a_list)
    print(len(tracks_a_list))

    tracks_link_list = [a.get('href') for a in tracks_a_list if a]

    if tracks_link_list:
        for link in tracks_link_list:
            print(link)
        print(len(tracks_link_list))
    else:
        print('something went wrong')

    return(tracks_link_list)

def write_to_database():
    for genre in list(GENRES_DICT.keys()):
        page_name = '{}.html'.format(GENRES_DICT[genre])
        track_list = get_50_from_genre(page_name)
        for track in track_list:
            db.add_song(track, genre)

if __name__ == '__main__':
    prepare_database(DB_FILENAME)
    write_to_database()

