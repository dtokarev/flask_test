import random
import time
import traceback

from sqlalchemy import func

from app_parser import db, app
from app_parser.domain.model import Search, Config, ResourceType, Download, ParsedData
from app_parser.domain.search import SearchPreferences
from app_parser.exception import NonCriticalException
from app_parser.scrapper import Rutracker

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))


def run():
    tracker.login()

    while True:
        if not _is_parser_active():
            _thread_sleep()
            continue

        s = _get_from_queue()

        if not s:
            app.logger.warn('no item to search')
            time.sleep(60)
            return

        _thread_sleep()
        search_and_parse(s)


def search_and_parse(s: Search):
    try:
        s.status = Search.Statuses.PROCESSING
        db.session.commit()

        preferences = SearchPreferences(keywords=[s.title_ru, s.title_en], year=s.year)

        link = tracker.get_page_link(preferences)
        _thread_sleep()
        raw_html = tracker.get_page_content(link)

        s.status = Search.Statuses.COMPLETED
        parsed_data = ParsedData.create_from(s, link, raw_html)
        db.session.add(parsed_data)
        db.session.add(Download.create_from(s, parsed_data))

    except Exception as e:
        db.session.rollback()
        s = Search.query.get(s.id)
        if isinstance(e, NonCriticalException):
            s.error = str(e)
            s.status = Search.Statuses.NOT_FOUND
        else:
            s.status = Search.Statuses.ERROR
            s.error = traceback.format_exc()
    finally:
        db.session.commit()


def _get_from_queue():
    s = Search.query\
        .filter_by(status=Search.Statuses.NEW, type=ResourceType.MOVIE)\
        .order_by(func.rand())\
        .first()
    return s


def _thread_sleep(lo: int =1, hi: int = 10):
    time.sleep(random.randint(lo, hi))


def _is_parser_active():
    is_active = Config.get('PARSER_IS_ACTIVE', bool)
    if not is_active:
        app.logger.warn('Parser stopped via configs')

    return is_active

run()
