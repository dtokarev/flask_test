import json

import requests

from app import db
from app.domain.model import Search, Config


def run():
    sources = [
        Config.get('EXTERNAL_MOVIE_SOURCE')
    ]

    for source in sources:
        response = requests.get(source).text
        # with open('tmp/mw.json', 'r') as file:
        #     response = file.read()
        print('received')

        data = json.loads(response)
        existing_ids = set(int(s.kinopoisk_id) for s in db.session.query(Search.kinopoisk_id).all())
        movies = data.get('report', {}).get('movies', [])

        for movie in movies:
            kinopoisk_id = movie.get('kinopoisk_id', None)

            if not kinopoisk_id or kinopoisk_id in existing_ids or kinopoisk_id < 1:
                continue

            existing_ids.add(kinopoisk_id)
            model_attributes = {
                'title_ru': movie.get('title_ru', ''),
                'title_en': movie.get('title_en', ''),
                'kinopoisk_id': kinopoisk_id,
                'year': movie.get('year', None),
                'type': Search.types.index('movie'),
                'import_source': 'all_en',
                'extra_json': movie,
            }
            db.session.add(Search(**model_attributes))

        print('adding new {}'.format(len(db.session.new)))
        db.session.commit()


run()
