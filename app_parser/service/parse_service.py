from app_parser.domain.model import Search, ParsedData, Download
from app_parser.scrapper import Rutracker


def create_parsed_data(s: Search, link, raw_html) -> ParsedData:
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