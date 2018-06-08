from nose.tools import assert_true, assert_false, assert_is

from app.domain.search import SearchPreferences, Matcher
from app.service.search_service import get_matcher
from app.utils.search import generate_keywords

preferences = SearchPreferences(keywords=['The Shawshank Redemption'], year='1994')
preferences.acceptable_size_range = '1.3 GB', '1.6 GB'


def test_matcher():
    matcher = get_matcher(
        preferences,
        {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption'
        })

    assert_true(matcher.acceptable_size_matched)
    assert_true(matcher.min_seeders_matched)

    matcher = get_matcher(
        preferences,
        {
            SearchPreferences.KEY_SIZE: '1.9 GB',
            SearchPreferences.KEY_SEEDERS: 1,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption'
        })
    assert_false(matcher.min_seeders_matched)


def test_best_matcher():
    matchers = []

    matcher1 = get_matcher(preferences, {
        SearchPreferences.KEY_SIZE: '1.9 GB',
        SearchPreferences.KEY_SEEDERS: 10,
        SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption'
    })
    matchers.append(matcher1)
    matcher2 = get_matcher(
        preferences,
        {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption'
        })
    matchers.append(matcher2)
    matcher3 = get_matcher(
        preferences,
        {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption'
        })
    matchers.append(matcher3)

    # first with best quality
    assert_is(matcher2, Matcher.get_best(matchers))

    # prepend to list
    matcher4 = get_matcher(
        preferences,
        {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption'
        })
    matchers = [matcher4] + matchers
    assert_is(matcher4, Matcher.get_best(matchers))

    # many seeders
    matcher5 = get_matcher(
        preferences,
        {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 1000,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption'
        })
    matchers.append(matcher5)
    assert_is(matcher5, Matcher.get_best(matchers))
