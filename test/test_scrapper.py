import random
from time import sleep

from nose.tools import *

from app.domain.dto import DecoupledParsedData
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


@with_setup(setup_func)
def test_rutr_login():
    assert_true(tracker.is_logged())


@with_setup(setup_func)
def test_rutr_parsers():
    link = tracker.get_page_link(['movie lorem ipsum dolor 2000'], preferences)
    assert_is_none(link)

    search_keys = generate_keywords('The Shawshank Redemption', '1994')
    link = tracker.get_page_link(search_keys, preferences)
    assert_is_not_none(link)

    # size
    page_data = Rutracker.parse_html(tracker.get_page_content(link))
    empty_data = DecoupledParsedData()

    size_current = size_human_to_float(page_data.size, 'KB')
    size_lo = size_human_to_float(preferences.acceptable_size_range[0], 'KB')
    size_hi = size_human_to_float(preferences.acceptable_size_range[1], 'KB')
    assert_true(size_lo <= size_current <= size_hi)

    assert_is_not(page_data.magnet_link, empty_data.magnet_link)
    assert_is_not(page_data.title, empty_data.title)
    assert_is_not(page_data.size, empty_data.size)
    assert_is_not(page_data.raw_data, empty_data.raw_data)
    assert_is_not(page_data.raw_html, empty_data.raw_html)

    assert_true(link.endswith('5460105'))




