import random
import time
import traceback

from sqlalchemy import func

from app import db
from app.domain.dto import ParsedData
from app.domain.model import Search, Config, Download
from app.domain.search import Preferences
from app.scrapper import Rutracker
from app.utils.search import generate_keywords

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))


def run():
    s = _get_from_queue()

    if not s:
        print('no item to search')
        time.sleep(60)
        return

    s_id = s.id
    try:
        s.status = Search.statuses.index('processing')
        db.session.commit()

        tracker.login()
        _thread_sleep()

        link = tracker.get_page_link(generate_keywords(s.title_ru, s.year), Preferences())
        _thread_sleep()

        raw_html = tracker.get_page_content(link)
        data = Rutracker.parse_html(raw_html)

        if not data:
            s.status = Search.statuses.index('not found')
            return

        s.page_link = link
        s.status = Search.statuses.index('completed')

        add_resource_meta(s, data)
        add_download(s, data)
    except Exception as e:
        db.session.rollback()
        s = Search.query.get(s_id)
        s.error = traceback.format_exc()
        s.status = Search.statuses.index('error')
        raise e
    finally:
        db.session.commit()


def add_resource_meta(search: Search, data: ParsedData) -> None:
    model = data.to_meta_model()
    model.search_id = search.id
    model.kinopoisk_id = search.kinopoisk_id
    model.title_en = search.title_en
    model.title_ru = search.title_ru
    model.import_source_id = search.get_from_raw('token')
    model.year = search.year

    db.session.add(model)


def add_download(search: Search, data: ParsedData) -> None:
    model = data.to_download_model()
    model.search_id = search.id
    model.progress = 0
    model.save_path = '/tmp/movies'
    model.status = Download.statuses.index('new')

    db.session.add(model)


def _get_from_queue():
    while True:
        s = Search.query.filter_by(status=Search.statuses.index('new')).order_by(func.rand()).first()
        if len(s.title_ru) > 5:
            break

    return s


def _thread_sleep(lo: int =1, hi: int = 3):
    time.sleep(random.randint(lo, hi))

run()
