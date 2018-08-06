from time import sleep

from app_parser import db
from app_parser.domain.Enum import FileTypes, ResourceType
from app_parser.domain.model import Download, Episode
from app_parser.utils.system import get_file_info_recursive, guess_type


def run():
    while True:
        d = get_from_queue()
        if not d:
            print('no completed downloads')
            sleep(20)
            continue

        print('decomposing', d.id)
        search = d.search
        parsed = search.parsed_data

        meta = {
            'kinopoisk_id': search.kinopoisk_id,
            # 'season_title': search.title_ru,
            # 'season_no': search.season_number,
            'episode_title': search.title_ru,
            'year': search.year,
            'search_id': search.id,
            'type': search.type,
            'genre': search.get_from_raw('genre', parsed.genre),
            'country': search.get_from_raw('country', parsed.country),
            'description': search.get_from_raw('description', parsed.description),
            'duration': parsed.duration,
            'translation': parsed.translation,
        }

        # TODO: добавить логику для сезонов
        for file_info in get_file_info_recursive(d.save_path):
            mime = file_info.get('mime')
            extension = file_info.get('extension')
            file_type = guess_type(extension, mime)
            file_meta = {
                    'mime': file_info.get('mime'),
                    'extension': file_info.get('extension'),
                    'system_path': file_info.get('path'),
                    'parent_folder': file_info.get('parent'),
                }
            file_meta.update(meta)

            if file_type is FileTypes.VIDEO:
                episode = Episode.create(file_meta)
                db.session.add(episode)
            elif file_type is not FileTypes.JUNK:
                pass
                # TODO: episode resources

        d.status = Download.Statuses.DECOMPOSED
        db.session.commit()


def get_from_queue() -> Download:
    db.session.close()
    return Download.query\
        .filter_by(status=Download.Statuses.COMPLETED, type=ResourceType.MOVIE)\
        .first()

run()
