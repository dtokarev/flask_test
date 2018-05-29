import json
import os
import pickle
import re

import requests
from bs4 import BeautifulSoup


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
        """
        logs current session
        """
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

    def search(self, key: str) -> dict:
        """
        :param key: search key
        :return: parsed data
        """
        link = Rutracker.URL_PAGE + self.get_page_link(key)
        parsed_data = self.parse_page_data(link)
        # print(json.dumps(parsed_data, indent=2, ensure_ascii=False))

        return parsed_data

    def parse_page_data(self, link: str) -> dict:
        """
        :param link: page link
        :return: parsed data from the page with magnet-link
        """
        data = {}
        response = self.session.get(link)
        bs = BeautifulSoup(response.content, "html.parser")
        data['magnet-link'] = bs.find('a', {'class': 'magnet-link'})['href']
        data['title'] = bs.find('span', {'class': 'post-u'}).get_text()

        body = bs.find('div', {'class': 'post_body'})

        for e in re.findall(r'(.+?) *: *(.+)', body.get_text()):
            k, v = e
            k = k.replace('\xa0', '').replace('\xa0', '').strip(' :')
            v = v.strip(' :|')
            data[k] = v

        return data

    def get_page_link(self, key) -> str:
        """
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

        for row in result.select('tbody > tr'):
            link_element = row.find('div', {'class': 't-title'}).find('a')
            title = link_element.get_text()
            link = link_element['href']
            # TODO: доп логика фильтрации
            return link

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

