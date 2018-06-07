import os
import random
from time import sleep

from nose.tools import *

from app.domain.model import Config
from app.domain.search import SearchPreferences
from app.scrapper import Rutracker
from app.utils.search import generate_keywords
from app.utils.unit_converter import size_human_to_float

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
    link = tracker.get_page_link(SearchPreferences(['movie lorem ipsum dolor 2000']))
    assert_is_none(link)

    link = tracker.get_page_link(SearchPreferences(generate_keywords('The Shawshank Redemption', '1994')))
    assert_is_not_none(link)

    assert_true(link.endswith('5460105'))


def test_rutr_parsed_data():
    folder = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(folder, 'data', 'rutr_page_html.html')) as file:
        html = file.read()

    parsed_data = Rutracker.parse_html(html)
    preferences = SearchPreferences(generate_keywords('Захват: Маршрут 300', '2018'))

    size_lo = size_human_to_float(preferences.acceptable_size_range[0], 'KB')
    size_hi = size_human_to_float(preferences.acceptable_size_range[1], 'KB')
    assert_true(size_lo <= parsed_data.size <= size_hi)

    assert_is_not_none(parsed_data.raw_data)
    assert_is_not_none(parsed_data.raw_html)

    assert_equal(parsed_data.magnet_link, 'magnet:?xt=urn:btih:B1C95EB63BB00A1A31A29FEE1EA6D9021D048A0D&tr=http%3A%2F%2Fbt.t-ru.org%2Fann%3Fmagnet')
    assert_equal(parsed_data.title, 'Захват: Маршрут 300 / Chatifa: Kav 300 (Ротем Шамир / Rotem Shamir) [2018, Израиль, драма, HDTVRip] + Sub Rus, Heb + Original Heb :: RuTracker.org')
    assert_equal(parsed_data.size, 1530920)

    assert_equal(parsed_data.country, 'Израиль')
    assert_equal(parsed_data.quality, 'HDTVRip')
    assert_equal(parsed_data.format, 'AVI')
    assert_equal(parsed_data.duration, 4401)
    assert_equal(parsed_data.translation, 'Субтитры')
    assert_equal(parsed_data.subtitle, 'русские (softsub, ASS), иврит (hardsub)')
    assert_equal(parsed_data.subtitle_format, 'softsub (ASS)')
    assert_equal(parsed_data.gender, 'драма')
