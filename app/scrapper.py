import os
import pickle
import re
from typing import Union

import requests
from bs4 import BeautifulSoup

from app.domain.dto import ParsedData
from app.domain.search import *
from app.services.search import get_matcher
from app.utils.unit_converter import duration_human_to_sec


class Rutracker:
    URL_BASE = "https://rutracker.net/"
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
        if self._load_session():
            return

        data = {
            'redirect': 'index.php',
            'login_username': self.user,
            'login_password': self.password,
            'login': '%C2%F5%EE%E4'
        }
        self.session.post(Rutracker.URL_LOGIN_POST, data)
        self._save_session()

    def is_logged(self) -> bool:
        response = self.session.get(self.URL_BASE)
        bs = BeautifulSoup(response.content, "html.parser")
        return bool(bs.find('a', {'href': '#pms-menu'}))

    # def solve_captcha(self):
    #     pass

    def get_page_link(self, keys: List[str], preferences: Preferences) -> Union[str, None]:
        """
        Accepts list of keys. If result page has any entry with currently iterated key returns best link,
        else picks up next key in list. So, order of the list is important, first item must be most specific,
        last most generic
        :param preferences:
        :param keys: search key list
        :return: link to page
        """
        for key in keys:
            content = self.get_search_result_content(key)
            link = self._get_page_link_from_search_result(content, preferences)

            if link:
                return link

        return None

    def get_search_result_content(self, key: str):
        post_data = {
            'nm': key,
            'prev_new': 0,
            'prev_oop': 0,
            # 'f[]': [7, 22],      # Category filter
            'o': 10,  # Sort by seeds number
            's': 2,
            'pn': None,
        }
        response = self.session.post(self.URL_SEARCH.format(key=key), post_data)
        print("search {} status code {}".format(key, response.status_code))

        return response.content

    def get_page_content(self, link: str):
        if not link:
            return None

        print('parsing link {}'.format(link))
        response = self.session.get(link)
        html = response.text
        html = re.sub(r'<hr[^>]+>', '\n', html)

        return html

    @staticmethod
    def parse_html(html: str) -> ParsedData:
        """
        :param html:
        :return: parsed data from the page with magnet-link
        """
        bs = BeautifulSoup(html, "html.parser")

        raw_data = {}
        body_text = str(bs.find('div', {'class': 'post_body'}))
        body_text = body_text\
            .replace('<br>', '\n')\
            .replace('<br/>', '\n')\
            .replace('\n\n', '\n')\
            .replace('<span class="post-br">\n</span>', '\n')

        for k, v in re.findall(r'<span class="post-b">(.*)</span>[ :]+(.+)', body_text):
            k = k.strip(' :|')
            v = re.sub(r'<[^>]+>', '', v.strip(' :|'))
            raw_data[k] = v

        data = ParsedData()
        data.raw_data = raw_data
        data.raw_html = html
        data.magnet_link = bs.find('a', {'class': 'magnet-link'})['href']
        data.title = bs.find('title')
        data.size = bs.find('span', {'id': 'tor-size-humn'}).get_text()

        data.country = raw_data.get('Страна')
        data.format = raw_data.get('Формат видео')
        data.duration = duration_human_to_sec(raw_data.get('Продолжительность'))
        data.translation = raw_data.get('Перевод')
        data.subtitle = raw_data.get('Субтитры')
        data.subtitle_format = raw_data.get('Формат субтитров')
        data.gender = raw_data.get('Жанр')
        data.description = raw_data.get('Описание')
        data.quality = raw_data.get('Качество видео')
        data.casting = raw_data.get('В ролях')
        data.video_info = raw_data.get('Видео')
        data.audio_info = raw_data.get('Аудио')

        return data

    @staticmethod
    def _get_page_link_from_search_result(html: str, preferences: Preferences) -> Union[str, None]:
        bs = BeautifulSoup(html, "html.parser")
        result = bs.find('table', {'id': 'tor-tbl'})

        matchers = []
        for row in result.select('tbody > tr'):
            size_tag = row.find('td', {'class': 'tor-size'})
            if not size_tag:
                return None

            actual_data = {
                Preferences.KEY_SIZE: size_tag.get_text()
            }

            # check size, format etc
            matcher = get_matcher(preferences, actual_data)
            matcher.bind_link(row.find('div', {'class': 't-title'}).find('a')['href'])
            matchers.append(matcher)

        return Rutracker.URL_PAGE + Matcher.get_best(matchers).link

    def _save_session(self):
        """
        saves serialized session to file
        """
        with open(self.SESSION_FILE, 'wb') as file:
            print("session saved to file")
            pickle.dump(self.session, file, pickle.HIGHEST_PROTOCOL)

    def _load_session(self) -> bool:
        """
        deserializes session from file
        :return: True if session is valid
        """
        if not self._is_session_present():
            return False

        with open(self.SESSION_FILE, 'rb') as file:
            print("session loaded from file")
            self.session = pickle.load(file)
            return self.is_logged()

    def _clear_session(self):
        if self._is_session_present():
            os.remove(self.SESSION_FILE)

    def _is_session_present(self):
        return os.path.isfile(self.SESSION_FILE)

