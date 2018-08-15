from nose.tools import assert_true, assert_is

from app_parser.domain.search import SearchPreferences, Matcher
from app_parser.service.parse_service import create_matcher

preferences = SearchPreferences(keywords=['The Shawshank Redemption'], year=1994)
preferences.acceptable_size_range = '1.3 GB', '1.6 GB'


def test_matcher():
    matcher = create_matcher(preferences, {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
        }, '')

    assert_true(matcher.acceptable_size_matched)
    assert_true(matcher.min_seeders_matched)

    matcher = create_matcher(preferences, {
            SearchPreferences.KEY_SIZE: '1.9 GB',
            SearchPreferences.KEY_SEEDERS: 2,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
        }, '')
    assert_true(matcher.min_seeders_matched)


def test_best_matcher():
    matchers = []

    matcher1 = create_matcher(preferences, {
        SearchPreferences.KEY_SIZE: '1.9 GB',
        SearchPreferences.KEY_SEEDERS: 10,
        SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
        SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
        }, '')

    matchers.append(matcher1)
    matcher2 = create_matcher(preferences, {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 10,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
        }, '')

    matchers.append(matcher2)
    matcher3 = create_matcher(preferences, {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 2,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
        }, '')

    matchers.append(matcher3)
    assert_is(matcher2, Matcher.get_best(matchers)[0])

    # many seeders
    matcher5 = create_matcher(preferences, {
            SearchPreferences.KEY_SIZE: '1.4 GB',
            SearchPreferences.KEY_SEEDERS: 1000,
            SearchPreferences.KEY_KEYWORD: 'The Shawshank Redemption',
            SearchPreferences.KEY_CATEGORY_NAME: 'Фильмы 2018',
        }, '')
    matchers.append(matcher5)
    assert_is(matcher5, Matcher.get_best(matchers)[0])
