import os
import random
from time import sleep

from nose.tools import *

from app_parser.domain.model import Config
from app_parser.domain.search import SearchPreferences
from app_parser.scrapper import Rutracker
from app_parser.utils.unit_converter import size_human_to_float

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))


def setup_func():
    sleep(random.randint(2, 4))
    tracker.login()


@nottest
@with_setup(setup_func)
def test_rutr_login():
    assert_true(tracker.is_logged())


@nottest
@with_setup(setup_func)
def test_rutr_search_link():
    matches = tracker.get_matches(SearchPreferences(['movie lorem ipsum dolor 2000']))
    assert_is_none(matches)

    matches = tracker.get_matches(SearchPreferences(['The Shawshank Redemption'], year=1994))
    assert_is_not_none(matches)

    assert_true(matches[0].link.endswith('5460105'))


def read_from_file(rel_path:str) -> str:
    folder = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(folder, rel_path)) as file:
        html = file.read()

    return html


def test_rutr_parsed_data():
    # 1 normal
    html = read_from_file(os.path.join('data', 'rutr_tdp_1.html'))
    parsed_data = Rutracker.parse_html(html)
    preferences = SearchPreferences(['Захват: Маршрут 300'], 2018)

    size_lo = size_human_to_float(preferences.acceptable_size_range[0], 'KB')
    size_hi = size_human_to_float(preferences.acceptable_size_range[1], 'KB')
    assert_true(size_lo <= parsed_data.size <= size_hi)

    assert_is_not_none(parsed_data.raw_page_data)

    assert_equal(parsed_data.magnet_link, 'magnet:?xt=urn:btih:B1C95EB63BB00A1A31A29FEE1EA6D9021D048A0D&tr=http%3A%2F%2Fbt.t-ru.org%2Fann%3Fmagnet')
    assert_equal(parsed_data.title, 'Захват: Маршрут 300 / Chatifa: Kav 300 (Ротем Шамир / Rotem Shamir) [2018, Израиль, драма, HDTVRip] + Sub Rus, Heb + Original Heb :: RuTracker.org')
    assert_equal(parsed_data.size, 1460000)

    assert_equal(parsed_data.country, 'Израиль')
    assert_equal(parsed_data.quality, 'HDTVRip')
    assert_equal(parsed_data.format, 'AVI')
    assert_equal(parsed_data.duration, 4401)
    assert_equal(parsed_data.translation, 'Субтитры')
    assert_equal(parsed_data.subtitle, 'русские (softsub, ASS), иврит (hardsub)')
    assert_equal(parsed_data.subtitle_format, 'softsub (ASS)')
    assert_equal(parsed_data.genre, 'драма')

    # 2 little difference in styles
    html = read_from_file(os.path.join('data', 'rutr_tdp_2.html'))
    parsed_data = Rutracker.parse_html(html)

    assert_equal(parsed_data.size, 1390000)
    assert_equal(parsed_data.country, 'Южная Корея')
    assert_equal(parsed_data.quality, 'WEB-DL')
    assert_equal(parsed_data.format, 'AVI')
    assert_equal(parsed_data.duration, 6220)
    assert_equal(parsed_data.translation, 'Любительский (многоголосый закадровый)')
    assert_equal(parsed_data.genre, 'романтика, комедия, мелодрама')

    # 3 little difference in styles
    html = read_from_file(os.path.join('data', 'rutr_tdp_3.html'))
    parsed_data = Rutracker.parse_html(html)

    assert_equal(parsed_data.size, 1460000)
    assert_equal(parsed_data.country, 'США / Paramount Pictures')
    # assert_equal(parsed_data.quality, 'WEB-DL')
    assert_equal(parsed_data.format, 'AVI')
    assert_equal(parsed_data.duration, 7282)
    assert_equal(parsed_data.translation, 'Профессиональный (полное дублирование) BD EUR |Лицензия')
    assert_equal(parsed_data.genre, 'боевик, драма, комедия')


def test_get_page_link_from_search_result():
    html = read_from_file(os.path.join('data', 'rutr_srp_1.html'))

    preferences = SearchPreferences(['Одержимая'], 2013)
    links = Rutracker.get_matches_from_search_result(html, preferences)
    assert_true(links[0].link.endswith('4734868'))

    preferences = SearchPreferences(['Одержимая'], 2013, acceptable_size_range=('3 GB', '4 GB'))
    links = Rutracker.get_matches_from_search_result(html, preferences)
    assert_true(links[0].link.endswith('5473278'))

    html = read_from_file(os.path.join('data', 'rutr_srp_2.html'))
    preferences = SearchPreferences(['Квартира', 'The Apartment'], 1960)
    links = Rutracker.get_matches_from_search_result(html, preferences)
    assert_true(links[0].link.endswith('2243255'))
