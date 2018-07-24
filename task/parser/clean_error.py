from app_parser import db
from app_parser.domain.model import Search


def run():
    _clean_hanged_downloads()


def _clean_hanged_downloads():
    searches = Search.query\
        .filter_by(status=Search.Statuses.ERROR)\
        .all()

    if not searches:
        return

    for search in searches:
        search.status = Search.Statuses.NEW
        print('search {} status returned to NEW '.format(search.id))

    db.session.commit()


run()
