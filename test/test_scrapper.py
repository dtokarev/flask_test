import os
import random
from time import sleep

from app import app
from nose.tools import *

from app.domain.dto import ParsedData
from app.domain.model import Config
from app.domain.search import Preferences
from app.scrapper import Rutracker
from app.utils.search import generate_keywords
from app.utils.unit_converter import size_human_to_float

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))
preferences = Preferences()


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
    link = tracker.get_page_link(['movie lorem ipsum dolor 2000'], preferences)
    assert_is_none(link)

    search_keys = generate_keywords('The Shawshank Redemption', '1994')
    link = tracker.get_page_link(search_keys, preferences)
    assert_is_not_none(link)

    assert_true(link.endswith('5460105'))


def test_rutr_parsed_data():
    folder = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(folder, 'data', 'rutr_page_html.html')) as file:
        html = file.read()

    parsed_data = Rutracker.parse_html(html)
    empty_data = ParsedData()

    size_current = size_human_to_float(parsed_data.size, 'KB')
    size_lo = size_human_to_float(preferences.acceptable_size_range[0], 'KB')
    size_hi = size_human_to_float(preferences.acceptable_size_range[1], 'KB')
    assert_true(size_lo <= size_current <= size_hi)

    assert_is_not(parsed_data.magnet_link, empty_data.magnet_link)
    assert_is_not(parsed_data.title, empty_data.title)
    assert_is_not(parsed_data.size, empty_data.size)
    assert_is_not(parsed_data.raw_data, empty_data.raw_data)
    assert_is_not(parsed_data.raw_html, empty_data.raw_html)

