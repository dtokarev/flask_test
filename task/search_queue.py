import json
import time
import traceback

from sqlalchemy import func

from app import db
from app.domain.model import Search, Config
from app.domain.search_preferences import Preferences
from app.scrapper import Rutracker
from app.utils.search import generate_keyword_set

tracker = Rutracker(Config.get("RUTR_USER"), Config.get("RUTR_PASS"))


def search():
    while True:
        s = Search.query.filter_by(status=Search.statuses.index('new')).order_by(func.rand()).first()
        if len(s.title_ru) > 5:
            break

    if not s:
        print('no item to search')
        time.sleep(60)
        return

    s_id = s.id
    try:
        s.status = Search.statuses.index('processing')
        db.session.commit()

        tracker.login()
        time.sleep(3)

        # generating keywords
        search_keys = generate_keyword_set(s.title_ru, s.year)
        search_preferences = Preferences()

        # searching the link
        best_link = None
        for search_key in search_keys:
            best_link = tracker.get_page_link(search_key, search_preferences)

        # parsing data
        data = tracker.parse_page(best_link)

        if not best_link or not data:
            s.status = Search.statuses.index('not found')
            return

        s.parsed_page = best_link
        s.status = Search.statuses.index('completed')
        add_download(data)

    except Exception as e:
        db.session.rollback()
        s = Search.query.get(s_id)
        s.error = traceback.format_exc()
        s.status = Search.statuses.index('error')
        raise e

    finally:
        db.session.commit()


def add_download(parsed_data: dict) -> None:
    print(json.dumps(parsed_data, indent=2))


search()
