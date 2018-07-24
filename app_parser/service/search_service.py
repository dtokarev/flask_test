import json

from app_parser.domain.model import Search, ResourceType


def create_from_mw(movie: dict, source_name: str, r_type: ResourceType) -> Search:
    s = Search()
    s.title_ru = movie.get('title_ru')
    s.title_en = movie.get('title_en')
    s.kinopoisk_id = movie.get('kinopoisk_id')
    s.import_source = source_name
    s.import_source_id = movie.get('token')
    s.year = movie.get('year')
    s.type = r_type
    s.raw = json.dumps(movie, ensure_ascii=False)
    return s
