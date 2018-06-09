import random
import time
import traceback

from sqlalchemy import func

from app_parser import db
from app_parser.domain.model import Search, Config, Download, ParsingStatus, ParsedData
from app_parser.domain.search import SearchPreferences
from app_parser.exception import NonCriticalException
from app_parser.scrapper import Rutracker

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))


def run():
    tracker.login()

    while True:
        s = _get_from_queue()

        if not s:
            print('no item to search')
            time.sleep(60)
            return

        _thread_sleep()
        search_and_parse(s)


def search_and_parse(s):
    s_id = s.id
    try:
        s.status = ParsingStatus.PROCESSING
        db.session.commit()

        preferences = SearchPreferences(keywords=[s.title_ru, s.title_en], year=s.year)
        link = tracker.get_page_link(preferences)
        _thread_sleep()

        raw_html = tracker.get_page_content(link)
        parsed_data = Rutracker.parse_html(raw_html)
        parsed_data.page_link = link

        s.status = ParsingStatus.COMPLETED
        save_parsed_data(s, parsed_data)
        add_download(s, parsed_data)
    except Exception as e:
        db.session.rollback()
        s = Search.query.get(s_id)
        if isinstance(e, NonCriticalException):
            s.error = str(e)
            s.status = ParsingStatus.NOT_FOUND
        else:
            s.status = ParsingStatus.ERROR
            s.error = traceback.format_exc()
    finally:
        db.session.commit()


def save_parsed_data(s: Search, parsed_data: ParsedData) -> None:
    parsed_data.search_id = s.id
    parsed_data.kinopoisk_id = s.kinopoisk_id
    parsed_data.title_en = s.title_en
    parsed_data.title_ru = s.title_ru
    parsed_data.import_source_id = s.import_source_id
    parsed_data.year = s.year

    db.session.add(parsed_data)


def add_download(s: Search, data: ParsedData) -> None:
    # TODO: refactor, send via REST to other microservice
    model = Download()
    model.magnet_link = data.magnet_link
    model.search_id = s.id
    model.progress = 0
    model.status = Download.STATUSES.index('new')

    db.session.add(model)


def _get_from_queue():
    while True:
        s = Search.query.filter_by(status=ParsingStatus.NEW).order_by(func.rand()).first()
        if len(s.title_ru) > 5:
            break

    return s


def _thread_sleep(lo: int =1, hi: int = 10):
    time.sleep(random.randint(lo, hi))


run()
