import unittest

from project.domain.search import SearchPreferences, Matcher
from project.service.parse_service import create_matcher
from project.service.scrapper import Rutracker
from project.utils.unit_converter import size_human_to_float
from test.unit.util.io import read_local_file


class TestMatcher(unittest.TestCase):
    def setUp(self):
        self.preferences = SearchPreferences(keywords=['The Shawshank Redemption'], year=1994)
        self.preferences.acceptable_size_range = '1.3 GB', '1.6 GB'

    def test_matcher(self):
        matcher = create_matcher(self.preferences, {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
        }, '')

        self.assertTrue(matcher.acceptable_size_matched)
        self.assertTrue(matcher.min_seeders_matched)

        matcher = create_matcher(self.preferences, {
            SearchPreferences.KEY_SIZE: '1.9 GB',
            SearchPreferences.KEY_SEEDERS: 2,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
        }, '')
        self.assertTrue(matcher.min_seeders_matched)

    def test_best_matcher(self):
        matchers = []

        matcher1 = create_matcher(self.preferences, {
            SearchPreferences.KEY_SIZE: '1.9 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
            SearchPreferences.KEY_TRANSLATION: 'dub',
        }, '')

        matchers.append(matcher1)
        matcher2 = create_matcher(self.preferences, {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
            SearchPreferences.KEY_TRANSLATION: 'dub',
        }, '')

        matchers.append(matcher2)
        matcher3 = create_matcher(self.preferences, {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 2,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
            SearchPreferences.KEY_TRANSLATION: 'dub',
        }, '')

        matchers.append(matcher3)
        self.assertIs(matcher2, Matcher.get_best(matchers)[0])

        # many seeders
        matcher5 = create_matcher(self.preferences, {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 1000,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
            SearchPreferences.KEY_TRANSLATION: 'dub',
        }, '')
        matchers.append(matcher5)
        self.assertIs(matcher5, Matcher.get_best(matchers)[0])


class TestScrapper(unittest.TestCase):
    def test_rutr_parsed_data(self):
        # 1 normal
        html = read_local_file('rutr', 'rutr_tdp_1.html')
        parsed_data = Rutracker.parse_html(html)
        preferences = SearchPreferences(['Захват: Маршрут 300'], 2018)

        size_lo = size_human_to_float(preferences.acceptable_size_range[0], 'KB')
        size_hi = size_human_to_float(preferences.acceptable_size_range[1], 'KB')
        self.assertTrue(size_lo <= parsed_data.size <= size_hi)

        self.assertIsNotNone(parsed_data.raw_page_data)

        self.assertEquals(parsed_data.magnet_link, 'magnet:?xt=urn:btih:B1C95EB63BB00A1A31A29FEE1EA6D9021D048A0D&tr=\http%3A%2F%2Fbt.t-ru.org%2Fann%3Fmagnet')
        self.assertEquals(parsed_data.title,'Захват: Маршрут 300 / Chatifa: Kav 300 (Ротем Шамир / Rotem Shamir) [2018, Израиль, драма, HDTVRip] + Sub Rus, Heb + Original Heb :: RuTracker.org')
        self.assertEquals(parsed_data.size, 1460000)

        self.assertEquals(parsed_data.country, 'Израиль')
        self.assertEquals(parsed_data.quality, 'HDTVRip')
        self.assertEquals(parsed_data.format, 'AVI')
        self.assertEquals(parsed_data.duration, 4401)
        self.assertEquals(parsed_data.translation, 'Субтитры')
        self.assertEquals(parsed_data.subtitle, 'русские (softsub, ASS), иврит (hardsub)')
        self.assertEquals(parsed_data.subtitle_format, 'softsub (ASS)')
        self.assertEquals(parsed_data.genre, 'драма')

        # different styles
        html = read_local_file('rutr', 'rutr_tdp_2.html')
        parsed_data = Rutracker.parse_html(html)

        self.assertEquals(parsed_data.size, 1390000)
        self.assertEquals(parsed_data.country, 'Южная Корея')
        self.assertEquals(parsed_data.quality, 'WEB-DL')
        self.assertEquals(parsed_data.format, 'AVI')
        self.assertEquals(parsed_data.duration, 6220)
        self.assertEquals(parsed_data.translation, 'Любительский (многоголосый закадровый)')
        self.assertEquals(parsed_data.genre, 'романтика, комедия, мелодрама')

        # different styles
        html = read_local_file('rutr', 'rutr_tdp_3.html')
        parsed_data = Rutracker.parse_html(html)

        self.assertEquals(parsed_data.size, 1460000)
        self.assertEquals(parsed_data.country, 'США / Paramount Pictures')
        self.assertEquals(parsed_data.format, 'AVI')
        self.assertEquals(parsed_data.duration, 7282)
        self.assertEquals(parsed_data.translation, 'Профессиональный (полное дублирование) BD EUR |Лицензия')
        self.assertEquals(parsed_data.genre, 'боевик, драма, комедия')

    def test_get_page_link_from_search_result(self):
        html = read_local_file('rutr', 'rutr_srp_1.html')

        preferences = SearchPreferences(['Одержимая'], 2013)
        links = Rutracker.get_matches_from_search_result(html, preferences)
        self.assertTrue(links[0].link.endswith('4734868'))

        preferences = SearchPreferences(['Одержимая'], 2013, acceptable_size_range=('3 GB', '4 GB'))
        links = Rutracker.get_matches_from_search_result(html, preferences)
        self.assertTrue(links[0].link.endswith('5473278'))

        html = read_local_file('rutr', 'rutr_srp_2.html')
        preferences = SearchPreferences(['Квартира', 'The Apartment'], 1960)
        links = Rutracker.get_matches_from_search_result(html, preferences)
        self.assertTrue(links[0].link.endswith('2243255'))