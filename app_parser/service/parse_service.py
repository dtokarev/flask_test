from app_parser.domain.model import Search, ParsedData, Download
from app_parser.domain.search import Matcher, SearchPreferences
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


def create_parsed_data(s: Search, link, raw_html) -> ParsedData:
    from app_parser.scrapper import Rutracker
    parsed_data = Rutracker.parse_html(raw_html)
    parsed_data.page_link = link
    parsed_data.search_id = s.id
    parsed_data.kinopoisk_id = s.kinopoisk_id
    parsed_data.title_en = s.title_en
    parsed_data.title_ru = s.title_ru
    parsed_data.import_source_id = s.import_source_id
    parsed_data.year = s.year

    return parsed_data


def create_download(s: Search, data: ParsedData) -> Download:
    # TODO: refactor, send via REST to other microservice
    download = Download()
    download.magnet_link = data.magnet_link
    download.search_id = s.id
    download.progress = 0
    download.status = Download.STATUSES.NEW

    return download