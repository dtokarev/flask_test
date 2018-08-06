import json
import requests

from app_parser import db
from app_parser.domain.model import Search, Config, ResourceType
from app_parser.service import search_service


def run():
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

        response = requests.get(source_url).text

        data = json.loads(response)
        existing_ids = set(int(s.kinopoisk_id) for s in db.session.query(Search.kinopoisk_id).all())

        for movie in data.get('report', {}).get(json_key, []):
            s = Search.create(movie, source_name, resource_type)

            if not s.kinopoisk_id or s.kinopoisk_id in existing_ids or s.kinopoisk_id < 1:
                continue

            existing_ids.add(s.kinopoisk_id)

            db.session.add(s)

        print('adding new {} {}'.format(source_name, len(db.session.new)))
        db.session.commit()


run()
