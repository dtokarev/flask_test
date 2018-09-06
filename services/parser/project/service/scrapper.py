import os
import pickle
import re
from typing import Union, Optional, Set, List, Tuple

import requests
from bs4 import BeautifulSoup

from project.domain.model import Config, ParsedData
from project.domain.search import SearchPreferences, Matcher
from project.domain.exception import ResultNotFoundException
from project.service.parse_service import create_matcher
from project.utils.dict import get_by_list
from project.utils.unit_converter import duration_human_to_sec, size_human_to_float


class Rutracker:
    URL_BASE = 'https://rutracker.net/'
    URL_LOGIN_POST = URL_BASE + 'forum/login.php'
    URL_SEARCH = URL_BASE + 'forum/tracker.php?nm={key}'
    URL_PAGE = URL_BASE + 'forum/'

    SESSION_FILE = "instance/tmp/session_rutracker"

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
        response = self.session.get(Rutracker.URL_BASE)
        bs = BeautifulSoup(response.content, "html.parser")
        return bool(bs.find('a', {'href': '#pms-menu'}))

    def get_all_matches(self, preferences: SearchPreferences) -> List[Matcher]:
        for key in preferences.generated_keywords:
            try:
                content = self.get_search_result_page(key)
                matches = self.get_matches_from_search_result(content, preferences)
            except (ResultNotFoundException, AttributeError) as e:
                continue

            if matches:
                return matches

        raise ResultNotFoundException('no link found for {}'.format(preferences))

    def get_search_result_page(self, key: str) -> bytes:
        """Html content of search page"""
        post_data = {
            'nm': key,
            'prev_new': 0,
            'prev_oop': 0,
            'o': 10,  # Sort by seeds number
            's': 2,
            'pn': None,
        }
        response = self.session.post(self.URL_SEARCH.format(key=key), post_data)

        return response.content

    def get_page_content(self, link: str) -> str:
        response = self.session.get(link)

        return response.text

    @staticmethod
    def parse_html(html: str) -> ParsedData:
        """
        :param html:
        :return: parsed data from the page with magnet-link
        """
        bs = BeautifulSoup(html, "html.parser")

        body_text = str(bs.find('div', {'class': 'post_body'}))
        body_text = re.sub(r'<hr[^>]+>', '\n', body_text)
        body_text = body_text.replace('<span class="post-b">', '\n<span class="post-b">')
        body_text = re.sub(r'<br/?>', '\n', body_text)
        # remove any tags with double colon
        body_text = re.sub(r'<[^>]+:[^>]+>([^<]+)<[^>]+>', r'\g<1>', body_text)
        body_text = re.sub(r'</span>:[\n\s]+', '</span>: ', body_text)
        body_text = re.sub(r':</span>[\n\s]+', '</span>: ', body_text)

        raw_data = {}
        for k, v in re.findall(r'<span class="post-b">(.*)</span>[ :]+(.+)', body_text):
            k = re.sub(r'<[^>]+>', ' ', k).strip(' :|')     # any tag to space
            k = re.sub(r'\s+', ' ', k)                       # multiple spaces to one

            v = re.sub(r'<[^>]+>', ' ', v).strip(' :|')
            v = re.sub(r'\s+', ' ', v).strip(' :|')
            raw_data[k] = v

        data = ParsedData()
        data.raw_page_data = raw_data
        data.magnet_link = bs.find('a', {'class': 'magnet-link'})['href']
        data.title = bs.find('title').get_text()
        data.size = int( size_human_to_float(bs.find('span', {'id': 'tor-size-humn'}).get_text(), 'KB') )

        data.country = get_by_list(raw_data, ['Страна', 'Выпущено'])
        data.format = get_by_list(raw_data, ['Формат видео', 'Формат'])
        data.duration = duration_human_to_sec(get_by_list(raw_data, ['Продолжительность']))
        data.translation = Rutracker.guess_translation(raw_data.get('Перевод'))
        data.subtitle = raw_data.get('Субтитры')
        data.subtitle_format = raw_data.get('Формат субтитров')
        data.genre = raw_data.get('Жанр')
        data.description = get_by_list(raw_data, ['Описание', 'О фильме'])
        data.quality = get_by_list(raw_data, ['Качество видео', 'Качество'])
        data.casting = raw_data.get('В ролях')
        data.video_info = raw_data.get('Видео')
        data.audio_info = raw_data.get('Аудио')

        return data

    @staticmethod
    def guess_translation(text) -> Optional[str]:
        if not text:
            return None

        return text

    @staticmethod
    def get_matches_from_search_result(html: Union[str, bytes], preferences: SearchPreferences) -> List[Matcher]:
        bs = BeautifulSoup(html, "html.parser")
        result = bs.find('table', {'id': 'tor-tbl'})

        matchers = []
        for row in result.select('tbody > tr'):
            size_tag = row.find('td', {'class': 'tor-size'})
            link_tag = row.find('a', {'class': 'tLink'})
            category_name = row.find('a', {'class': 'gen'})
            seeders_tag = row.find('b', {'class': 'seedmed'})
            seeders = int(seeders_tag.get_text()) if seeders_tag else 0
            link_info = re.search(r"(?P<title>.+)\s*\[(?P<info>.+)\]\s*(?P<translation>.+)", link_tag.get_text())
            link_info = link_info.groupdict() if link_info else {}
            link = Rutracker.URL_PAGE + row.find('div', {'class': 't-title'}).find('a')['href']

            if not size_tag:
                continue

            actual_data = {
                SearchPreferences.KEY_SIZE: size_tag.get_text(),
                SearchPreferences.KEY_SEEDERS: seeders,
                SearchPreferences.KEY_KEYWORD: link_info.get('title'),
                SearchPreferences.KEY_CATEGORY_NAME: category_name.get_text(),
                SearchPreferences.KEY_TRANSLATION: link_info.get('translation', 'ORIGINAL').split('+')[0].strip(),
            }

            matcher = create_matcher(preferences, actual_data, link)
            matchers.append(matcher)

        return matchers

    def _save_session(self):
        """
        saves serialized session to file
        """
        with open(self.SESSION_FILE, 'wb') as file:
            pickle.dump(self.session, file, pickle.HIGHEST_PROTOCOL)

    def _load_session(self) -> bool:
        """
        deserializes session from file
        :return: True if session is valid
        """
        if not self._is_session_present():
            return False

        with open(self.SESSION_FILE, 'rb') as file:
            self.session = pickle.load(file)
            return self.is_logged()

    def _clear_session(self):
        if self._is_session_present():
            os.remove(self.SESSION_FILE)

    def _is_session_present(self):
        return os.path.isfile(self.SESSION_FILE)
