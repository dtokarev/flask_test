import json
import requests
import time

from app_parser import db, app
from app_parser.domain.model import Search, Config, ResourceType


def run():
    existing_ids = set(int(s.kinopoisk_id) for s in db.session.query(Search.kinopoisk_id).all())

    while True:
        sources = {
            'movies_foreign': Config.get('FOREIGN_MOVIE_SOURCE'),
            'movies_russian': Config.get('RUSSIAN_MOVIE_SOURCE'),
            'series_foreign': Config.get('FOREIGN_SERIES_SOURCE'),
            'series_russian': Config.get('RUSSIAN_SERIES_SOURCE')
        }

        for source_name, source_url in sources.items():
            if source_name.startswith('series'):
                resource_type = ResourceType.SERIES
                json_key = 'serials'
            else:
                resource_type = ResourceType.MOVIE
                json_key = 'movies'

            response = requests.get(source_url)

            try:
                data = json.loads(response.text)
            except ValueError as e:
                app.logger.error('Can not parse {} \n {} \n {}'.format(source_url, response.status_code, e))
                continue

            for movie in data.get('report', {}).get(json_key, []):
                s = Search.create(movie, source_name, resource_type)

                if not s.kinopoisk_id or s.kinopoisk_id in existing_ids or s.kinopoisk_id < 1:
                    continue

                existing_ids.add(s.kinopoisk_id)

                db.session.add(s)

            app.logger.warn('adding new {} {}'.format(source_name, len(db.session.new)))
            db.session.commit()

        sleep_for = 4*3600
        app.logger.warn('sleep for {}'.format(sleep_for))
        time.sleep(sleep_for)


run()
