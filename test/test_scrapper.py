import random
from time import sleep

from nose.tools import *

from app.domain.model import Config
from app.scrapper import *
from app.utils.search import generate_keyword_set
from app.utils.unit_converter import size_human_to_float

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))
preferences = Preferences()
# preferences_big = Preferences(acceptable_size_range = ('2.1 GB', '2.2 GB'))


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

    search_keys = generate_keyword_set('The Shawshank Redemption', '1994')
    link = tracker.get_page_link(search_keys, preferences)
    assert_is_not_none(link)

    # size
    page_data = tracker.parse_page(link)
    size_current = size_human_to_float(page_data.get(ParserTokens.KEY_SIZE, '0 KB'), 'KB')
    size_lo = size_human_to_float(preferences.acceptable_size_range[0], 'KB')
    size_hi = size_human_to_float(preferences.acceptable_size_range[1], 'KB')
    assert_true(size_lo <= size_current <= size_hi)

    assert_is_not_none(page_data.get(ParserTokens.KEY_MAGNET_LINK))
    assert_is_not_none(page_data.get(ParserTokens.KEY_TITLE))
    assert_is_not_none(page_data.get(ParserTokens.KEY_SIZE))
    assert_is_not_none(page_data.get(ParserTokens.KEY_PAGE_LINK))

    assert_true(link.endswith('5460105'))




