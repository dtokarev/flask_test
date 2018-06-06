import random
import time
import traceback

from sqlalchemy import func

from app import db
from app.domain.dto import DecoupledParsedData
from app.domain.model import Search, Config, ParsedData, Download
from app.domain.search import Preferences
from app.scrapper import Rutracker, ParserTokens
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

        add_parsed_data(s, data)
        add_download(s, data)

    except Exception as e:
        db.session.rollback()
        s = Search.query.get(s_id)
        s.error = traceback.format_exc()
        s.status = Search.statuses.index('error')
        raise e

    finally:
        db.session.commit()


def add_parsed_data(search: Search, data: DecoupledParsedData) -> None:
    model = ParsedData(
        search_id=search.id,
        kinopoisk_id=search.kinopoisk_id,
        mw_id='',
        raw_page_data=data,
        raw_page_html=data.raw_html,
        quality='',
        format='',
        size=data.size,
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


def add_download(search: Search, data: DecoupledParsedData) -> None:
    model = Download(
        search_id=search.id,
        progress=0,
        magnet_link=data.magnet_link,
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


def _thread_sleep(lo: int =1, hi: int = 3):
    time.sleep(random.randint(lo, hi))

run()
