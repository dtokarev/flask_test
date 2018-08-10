from app_parser import db, app
from app_parser.domain.model import Search


def run():
    clean_hanged_downloads()


def clean_hanged_downloads():
    searches = Search.query\
        .filter_by(status=Search.Statuses.ERROR)\
        .all()

    if not searches:
        return

    for search in searches:
        search.status = Search.Statuses.NEW
        app.logger.warn('search {} status returned to NEW '.format(search.id))

    db.session.commit()


run()
