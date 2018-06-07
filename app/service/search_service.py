from app.domain.search import SearchPreferences, Matcher
from app.utils.unit_converter import size_human_to_float


def get_matcher(preferences: SearchPreferences, actual_data: dict):
    matcher = Matcher()

    # size
    size_unit = SearchPreferences.DEFAULT_UNIT
    current_size = size_human_to_float(actual_data[SearchPreferences.KEY_SIZE], size_unit)
    if current_size:
        acceptable_size_lo = size_human_to_float(preferences.acceptable_size_range[0], size_unit)
        acceptable_size_hi = size_human_to_float(preferences.acceptable_size_range[1], size_unit)
        matcher.acceptable_size_matched = acceptable_size_lo < current_size < acceptable_size_hi

    # seeders
    actual_seeders = actual_data.get(SearchPreferences.KEY_SEEDERS)
    if actual_seeders:
        matcher.min_seeders_matched = preferences.min_seeders <= actual_seeders
        matcher.seeders_num = actual_seeders

    # keyword (any keyword exists in actual_title)
    actual_title = str(actual_data.get(SearchPreferences.KEY_KEYWORD))
    for k in preferences.keywords:
        if k in actual_title:
            matcher.keyword_matched = True

    return matcher
