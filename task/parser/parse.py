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
            continue

        _thread_sleep()
        search_and_parse(s)


def search_and_parse(s: Search):
    try:
        s.status = Search.Statuses.PROCESSING
        db.session.commit()

        cnt = 4 if s.type == ResourceType.SERIES else 2
        preferences = SearchPreferences(keywords=[s.title_ru, s.title_en], year=s.year, cnt=cnt)

        matches = tracker.get_matches(preferences)

        for m in matches:
            _thread_sleep()
            app.logger.info('search_id {} - parsing link {}'.format(s.id, m.link))
            raw_html = tracker.get_page_content(m.link)

            s.status = Search.Statuses.COMPLETED
            parsed_data = ParsedData.create(s, m, raw_html)
            db.session.add(parsed_data)
            db.session.add(Download.create(parsed_data, s.type))

    except Exception as e:
        db.session.rollback()
        s = Search.query.get(s.id)
        if isinstance(e, NonCriticalException):
            app.logger.warn('search_id {} - {}'.format(s.id, e))
            s.error = str(e)
            s.status = Search.Statuses.NOT_FOUND
        else:
            app.logger.error('search_id {} - exception {}'.format(s.id, traceback.format_exc()))
            s.status = Search.Statuses.ERROR
            s.error = traceback.format_exc()
    finally:
        db.session.commit()


def _get_from_queue():
    s = Search.query\
        .filter_by(status=Search.Statuses.NEW, type=ResourceType.MOVIE)\
        .filter(func.length(Search.title_ru) > 10)\
        .order_by(func.rand())\
        .first()
    return s


def _thread_sleep(lo: int =1, hi: int = 10):
    time.sleep(random.randint(lo, hi))


def _is_parser_active():
    is_active = Config.get('PARSER_IS_ACTIVE', bool)
    # if not is_active:
    #     app.logger.warn('Parser stopped via configs')

    return is_active

run()
