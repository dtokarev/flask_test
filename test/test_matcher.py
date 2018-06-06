from nose.tools import *

from app.domain.search import Preferences, Matcher
from app.services.search import get_matcher

preferences = Preferences()
preferences.acceptable_size_range = '1.3 GB', '1.6 GB'


def test_matcher():
    matcher = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB'})
    assert_true(matcher.acceptable_size_matched)

    matcher = get_matcher(preferences, {Preferences.KEY_SIZE: '1.9 GB'})
    assert_false(matcher.acceptable_size_matched)


def test_best_matcher():
    matchers = []

    matcher1 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.9 GB'})
    matchers.append(matcher1)
    matcher2 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB'})
    matchers.append(matcher2)
    matcher3 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB'})
    matchers.append(matcher3)

    # first with best quality
    assert_is(matcher2, Matcher.get_best(matchers))

    # prepend to list
    matcher4 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB'})
    matchers = [matcher4] + matchers
    assert_is(matcher4, Matcher.get_best(matchers))
