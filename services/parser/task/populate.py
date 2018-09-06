import json
import time

import requests

from project import db
from . import cli
from project.domain.model import Config, ResourceType, Search
from flask import current_app as app


@cli.command()
def populate():
    """Populate search queue from external source"""
    existing_ids = set(int(s.kinopoisk_id) for s in db.session.query(Search.kinopoisk_id).all())

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
            data = data.get('updates', data.get('report', {}).get(json_key, []))
        except ValueError as e:
            app.logger.error('Can not parse {} \n {} \n {}'.format(source_url, response.status_code, e))
            continue

        for movie in data:
            s = Search.create(movie, source_name, resource_type)

            if not s.kinopoisk_id \
                    or s.kinopoisk_id in existing_ids:
                continue

            existing_ids.add(s.kinopoisk_id)
            db.session.add(s)

        app.logger.warning('adding new {} {}'.format(source_name, len(db.session.new)))
        db.session.commit()

        time.sleep(60*30)