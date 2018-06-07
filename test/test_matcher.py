from nose.tools import assert_true, assert_false, assert_is

from app.domain.search import Preferences, Matcher
from app.services.search import get_matcher

preferences = Preferences()
preferences.acceptable_size_range = '1.3 GB', '1.6 GB'


def test_matcher():
    matcher = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB', Preferences.KEY_SEEDERS: 10})
    assert_true(matcher.acceptable_size_matched)
    assert_true(matcher.min_seeders_matched)

    matcher = get_matcher(preferences, {Preferences.KEY_SIZE: '1.9 GB', Preferences.KEY_SEEDERS: 1})
    matcher = get_matcher(preferences, {Preferences.KEY_SIZE: '1.9 GB', Preferences.KEY_SEEDERS: 1})
    assert_false(matcher.min_seeders_matched)


def test_best_matcher():
    matchers = []

    matcher1 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.9 GB', Preferences.KEY_SEEDERS: 10})
    matchers.append(matcher1)
    matcher2 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB', Preferences.KEY_SEEDERS: 10})
    matchers.append(matcher2)
    matcher3 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB', Preferences.KEY_SEEDERS: 10})
    matchers.append(matcher3)

    # first with best quality
    assert_is(matcher2, Matcher.get_best(matchers))

    # prepend to list
    matcher4 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB', Preferences.KEY_SEEDERS: 10})
    matchers = [matcher4] + matchers
    assert_is(matcher4, Matcher.get_best(matchers))

    # many seeders
    matcher5 = get_matcher(preferences, {Preferences.KEY_SIZE: '1.4 GB', Preferences.KEY_SEEDERS: 1000})
    matchers.append(matcher5)
    assert_is(matcher5, Matcher.get_best(matchers))
