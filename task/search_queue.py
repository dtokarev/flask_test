import json
import time
import traceback

from sqlalchemy import func

import config
from app import db
from app.model import Search
from app.scrapper import Rutracker

USER = config.get_secret("RUTR_USER")
PASS = config.get_secret("RUTR_PASS")

tracker = Rutracker(USER, PASS)


def search():
    while True:
        s = Search.query.filter_by(status=Search.statuses.index('new')).order_by(func.rand()).first()
        if len(s.title_ru) > 5:
            break

    if not s:
        return

    s_id = s.id
    try:
        s.status = Search.statuses.index('processing')
        db.session.commit()
        tracker.login()
        time.sleep(3)
        data = tracker.search('{} {}'.format(s.title_ru, s.year))

        add_download(data)
    except Exception as e:
        db.session.rollback()
        s = Search.query.get(s_id)
        s.error = traceback.format_exc()
        s.status = Search.statuses.index('error')
    finally:
        db.session.commit()


def add_download(parsed_data: dict) -> None:
    print(parsed_data)


search()
