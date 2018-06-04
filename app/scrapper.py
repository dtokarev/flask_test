import os
import pickle
import re
from typing import Union

import requests
from bs4 import BeautifulSoup

from app.domain.model import ParsedData
from app.domain.search_preferences import *


class Rutracker:
    URL_BASE = "http://rutracker.net/"
    URL_LOGIN_POST = URL_BASE + "forum/login.php"
    URL_SEARCH = URL_BASE + "forum/tracker.php?nm={key}"
    URL_PAGE = URL_BASE + "forum/"

    SESSION_FILE = "tmp/session_rutracker"

    def __init__(self, user, password):
        self.user = user
        self.password = password

        self.base_headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'accept-encoding': ', '.join(('gzip', 'deflate')),
            'accept': ','.join(('text/html', '*/*')),
            'connection': 'keep-alive',
            'accept-language': 'ru,en;q=0.9',
            'cache-control': 'no-cache',
        }
        self.session = requests.session()
        self.session.headers = self.base_headers

    def login(self) -> None:
        if self.load_session():
            return

        data = {
            'redirect': 'index.php',
            'login_username': self.user,
            'login_password': self.password,
            'login': '%C2%F5%EE%E4'
        }
        self.session.post(Rutracker.URL_LOGIN_POST, data)
        self.save_session()

    def is_logged(self) -> bool:
        response = self.session.get(self.URL_BASE)
        bs = BeautifulSoup(response.content, "html.parser")
        return bool(bs.find('a', {'href': '#pms-menu'}))

    # def solve_captcha(self):
    #     pass

    def search(self, key: str, preferences: Preferences) -> dict:
        """
        searches for given key and preferences and returns parsed page data
        :param preferences: additional parameters for filtering search result set
        :param key: search key
        :return: parsed data
        """
        link = self.get_page_link(key, preferences)
        print('parsing link {} for search query {} '.format(link, key))

        return self.parse_page_data(link)

    def parse_page_data(self, link: str) -> Union[dict, None]:
        """
        :param link: page link
        :return: parsed data from the page with magnet-link
        """
        if not link:
            return None

        result = {}
        response = self.session.get(link)
        html = response.text
        html = re.sub(r'<hr[^>]+>', '\n', html)

        with open('tmp/html.txt', 'w') as file:
            file.write(html)

        bs = BeautifulSoup(html, "html.parser")

        body = bs.find('div', {'class': 'post_body'})

        for k, v in re.findall(r'(.+?) *: *(.+)', body.get_text()):
            k = k.replace('\xa0', '').strip(' :')
            v = v.strip(' :|')
            result[k] = v

        result['magnet-link'] = bs.find('a', {'class': 'magnet-link'})['href']
        result['title'] = bs.find('title').get_text()

        return result

    def get_page_link(self, key, preferences: Preferences) -> Union[str, None]:
        """
        :param preferences:
        :param key: search key
        :return: link to page
        """
        post_data = {
            'nm': key,
            'prev_new': 0,
            'prev_oop': 0,
            # 'f[]': [7, 22],      # Категория фильмы
            'o': 10,  # Количество сидов
            's': 2,
            'pn': None,
        }
        response = self.session.post(self.URL_SEARCH.format(key=key), post_data)
        print("search status code", response.status_code)

        bs = BeautifulSoup(response.content, "html.parser")
        result = bs.find('table', {'id': 'tor-tbl'})

        matchers = []
        for row in result.select('tbody > tr'):
            if not row.find('td', {'class': 'tor-size'}):
                return None

            result_data = {
                KEY_SIZE: row.find('td', {'class': 'tor-size'}).get_text()
            }

            # check size, format etc
            matcher = preferences.get_matcher(result_data)
            matcher.bind_link(row.find('div', {'class': 't-title'}).find('a')['href'])
            matchers.append(matcher)

        return Rutracker.URL_PAGE + Matcher.get_best(matchers).link

    def save_session(self):
        """
        saves serialized session to file
        """
        with open(self.SESSION_FILE, 'wb') as file:
            print("session saved to file")
            pickle.dump(self.session, file, pickle.HIGHEST_PROTOCOL)

    def load_session(self) -> bool:
        """
        deserializes session from file
        :return: True if session is logged
        """
        if not os.path.isfile(self.SESSION_FILE):
            return False

        with open(self.SESSION_FILE, 'rb') as file:
            print("session loaded from file")
            self.session = pickle.load(file)
            return self.is_logged()

