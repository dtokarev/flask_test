import random
import time
import traceback

from sqlalchemy import func

from app import db
from app.domain.model import Search, Config, ParsedData, Download
from app.domain.search_preferences import Preferences
from app.scrapper import Rutracker, ParserTokens
from app.utils.search import generate_keywords

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))


def run():
    s = _get_from_queue()
    search_preferences = Preferences()

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

        link = tracker.get_page_link(generate_keywords(s.title_ru, s.year), search_preferences)
        _thread_sleep()

        data, raw_html = tracker.parse_page(link)

        if not data:
            s.status = Search.statuses.index('not found')
            return

        s.parsed_page = link
        s.status = Search.statuses.index('completed')

        add_parsed_data(s, data, raw_html)
        add_download(s, data)

    except Exception as e:
        db.session.rollback()
        s = Search.query.get(s_id)
        s.error = traceback.format_exc()
        s.status = Search.statuses.index('error')
        raise e

    finally:
        db.session.commit()


def add_parsed_data(search: Search, data: dict, raw_html: str) -> None:
    model = ParsedData(
        search_id=search.id,
        kinopoisk_id=search.kinopoisk_id,
        mw_id='',
        raw_page_data=data,
        raw_page_html=raw_html,
        quality='',
        format='',
        size=data.get(ParserTokens.KEY_SIZE),
        title_en=search.title_en,
        title_ru=search.title_ru,
        duration='',
        translation='',
        subtitle='',
        subtitle_format='',
        gender='',
        description='',
        year='',
        casting='',
        video_info='',
        audio_info='',
    )
    db.session.add(model)


def add_download(search: Search, data: dict) -> None:
    model = Download(
        search_id=search.id,
        progress=0,
        magnet_link=data.get(ParserTokens.KEY_MAGNET_LINK),
        save_path='/tmp/movies',
        status=Download.statuses.index('new'),
    )
    db.session.add(model)


def _get_from_queue():
    while True:
        s = Search.query.filter_by(status=Search.statuses.index('new')).order_by(func.rand()).first()
        if len(s.title_ru) > 5:
            break

    return s


def _thread_sleep():
    time.sleep(random.randint(1, 3))

run()
