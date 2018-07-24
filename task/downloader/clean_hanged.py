import time
from datetime import datetime, timedelta

from app_parser import db
from app_parser.domain.model import Download


def run():
    while True:
        _clean_hanged_downloads()
        time.sleep(10)


def _clean_hanged_downloads():
    t = datetime.utcnow() - timedelta(minutes=10)
    downloads = Download.query\
        .filter_by(status=Download.Statuses.DOWNLOADING)\
        .filter(Download.changed_at < t)\
        .all()

    if not downloads:
        return

    for d in downloads:
        d.status = Download.Statuses.NEW
        print('download cleaned {}'.format(d.id))

    db.session.commit()


run()
