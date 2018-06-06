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

            s = Search()
            s.title_ru = movie.get('title_ru', None)
            s.title_en = movie.get('title_en', None)
            s.kinopoisk_id = kinopoisk_id
            s.year = movie.get('year', None)
            s.type = Search.types.index('movie')
            s.import_source = 'all_en'
            s.extra_json = json.dumps(movie)

            db.session.add(s)

        print('adding new {}'.format(len(db.session.new)))
        db.session.commit()


run()