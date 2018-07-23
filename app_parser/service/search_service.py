import json

from app_parser.domain.model import Search, ResourceType
from app_parser.domain.search import SearchPreferences, Matcher
from app_parser.utils.unit_converter import size_human_to_float


def create_matcher(preferences: SearchPreferences, actual_data: dict) -> Matcher:
    """
    Creates matcher from preferences and actual parsed data
    """
    matcher = Matcher()

    # size
    size_unit = SearchPreferences.DEFAULT_UNIT
    actual_size = size_human_to_float(actual_data[SearchPreferences.KEY_SIZE], size_unit)
    if actual_size:
        acceptable_size_lo = size_human_to_float(preferences.acceptable_size_range[0], size_unit)
        acceptable_size_hi = size_human_to_float(preferences.acceptable_size_range[1], size_unit)
        matcher.acceptable_size_matched = acceptable_size_lo < actual_size < acceptable_size_hi

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


def create_from_mw(movie: dict, source_name: str, r_type: ResourceType) -> Search:
    s = Search()
    s.title_ru = movie.get('title_ru')
    s.title_en = movie.get('title_en')
    s.kinopoisk_id = movie.get('kinopoisk_id')
    s.import_source = source_name
    s.import_source_id = movie.get('token')
    s.year = movie.get('year')
    s.type = r_type
    s.raw = json.dumps(movie, ensure_ascii=False)
    return s