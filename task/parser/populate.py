import json

import requests

from app_parser import db
from app_parser.domain.model import Search, Config, ResourceType


def run():
    sources = {
        'movies_foreign': Config.get('FOREIGN_MOVIE_SOURCE'),
        'movies_russian': Config.get('RUSSIAN_MOVIE_SOURCE')
    }

    for source_name, source_location in sources.items():
        # with open(source_location, 'r') as file:
        #     response = file.read()
        response = requests.get(source_location).text

        data = json.loads(response)
        existing_ids = set(int(s.kinopoisk_id) for s in db.session.query(Search.kinopoisk_id).all())

        movies = data.get('report', {}).get('movies', [])
        for movie in movies:
            kinopoisk_id = movie.get('kinopoisk_id')

            if not kinopoisk_id or kinopoisk_id in existing_ids or kinopoisk_id < 1:
                continue

            existing_ids.add(kinopoisk_id)

            s = Search()
            s.title_ru = movie.get('title_ru')
            s.title_en = movie.get('title_en')
            s.kinopoisk_id = kinopoisk_id
            s.import_source_id = movie.get('token')
            s.year = movie.get('year')
            s.type = ResourceType.MOVIE
            s.import_source = source_name
            s.raw = json.dumps(movie, ensure_ascii=False)

            db.session.add(s)

        print('adding new {}'.format(len(db.session.new)))
        db.session.commit()


run()
