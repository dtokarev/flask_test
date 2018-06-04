from app import app


@app.route("/import/mw-report", methods=["POST"])
def add_torrent():
    pass
    # response = requests.get(config.get_secret('EXTERNAL_MOVIE_SOURCE'))
    # print('received')
    #
    # data = json.loads(response.text)
    # movies = data.get('report', {}).get('movies', [])
    #
    # for movie in movies:
    #     model_attributes = {
    #        'title_ru': movie.get('title_ru', ''),
    #        'title_en': movie.get('title_en', ''),
    #        'kinopoisk_id': movie.get('kinopoisk_id', ''),
    #        'type': Search.types.index('movie'),
    #        'import_source': 'all_en',
    #        'extra_json': movie,
    #     }
    #     db.session.add(Search(**model_attributes))
    # db.session.commit()
    #
    # return 'added {}'.format(len(movies))
