import random
import time
import traceback

from sqlalchemy import func
from flask import current_app as app

from project import db, Search, ParsedData, redis, ResourceType
from project.domain.exception import NonCriticalException
from project.domain.model import Config
from project.domain.search import SearchPreferences, Matcher
from project.service.scrapper import Rutracker
from . import cli


@cli.command()
def parse():
    tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))
    tracker.login()

    if not _is_parser_active():
        _thread_sleep()
        return

    s = _get_from_queue()

    if not s:
        app.logger.warn('no item to search')
        time.sleep(60)
        return

    _thread_sleep()
    search_and_parse(s, tracker)


@cli.command()
def produce_downloads():
    parsed_datas = ParsedData.query \
        .filter_by(download_status=ParsedData.DownloadStatuses.NOT_SEND) \
        .join(Search) \
        .all()

    if not parsed_datas:
        time.sleep(60)
        return

    for parsed_data in parsed_datas:
        search = parsed_data.search
        data = {
            'parsed_data_id': parsed_data.id,
            'magnet': parsed_data.magnet_link,
            'type': search.type.value,
            'search_id': search.id,
            'force_update': False
        }

        redis.lpush('downloads', data)

        app.logger.info('send to downloads queue: {}'.format(str(data)))
        parsed_data.download_status = ParsedData.DownloadStatuses.SEND
        db.session.commit()


def search_and_parse(s: Search, tracker: Rutracker):
    try:
        s.status = Search.Statuses.PROCESSING
        db.session.commit()

        sample_count = SearchPreferences.get_default_sample_count_for_type(s.type)
        preferences = SearchPreferences(keywords=[s.title_ru, s.title_en], year=s.year, sample_count=sample_count)

        matches = tracker.get_all_matches(preferences)
        matches = Matcher.get_best(matches, preferences.sample_count)

        for m in matches:
            _thread_sleep()
            app.logger.info('search_id {} - parsing link {}'.format(s.id, m.link))
            raw_html = tracker.get_page_content(m.link)

            s.status = Search.Statuses.COMPLETED
            parsed_data = Rutracker.parse_html(raw_html)
            parsed_data = ParsedData.create(s, m, parsed_data=parsed_data)
            db.session.add(parsed_data)
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


def _get_from_queue() -> Search:
    s = Search.query\
        .filter_by(status=Search.Statuses.NEW, type=ResourceType.MOVIE)\
        .filter(func.length(Search.title_ru) > 10)\
        .order_by(func.rand())\
        .first()
    return s


def _thread_sleep(lo: int =1, hi: int = 10) -> None:
    time.sleep(random.randint(lo, hi))


def _is_parser_active() -> bool:
    is_active = Config.get('PARSER_IS_ACTIVE', bool)
    # if not is_active:
    #     app.logger.warn('Parser stopped via configs')

    return is_active
