from time import sleep

from app_parser import db, app
from app_parser.domain.Enum import FileTypes, ResourceType
from app_parser.domain.model import Download, Episode
from app_parser.utils.system import get_file_info_recursive, guess_type


def run():
    while True:
        d = get_from_queue()
        if not d:
            app.logger.warn('no completed downloads')
            sleep(20)
            continue

        app.logger.info('decomposing download.id={}'.format(d.id))
        search = d.search
        parsed_data = search.parsed_data

        meta = {
            'kinopoisk_id': search.kinopoisk_id,
            # 'season_no': search.season_number,
            'episode_title': search.title_ru,
            'year': search.year,
            'parsed_data_id': parsed_data.id,
            'type': search.type,
            'genre': search.get_from_raw('genre', parsed_data.genre),
            'country': search.get_from_raw('country', parsed_data.country),
            'description': search.get_from_raw('description', parsed_data.description),
            'duration': parsed_data.duration,
            'translation': parsed_data.translation_code,
        }

        # TODO: добавить логику для сезонов
        for file_info in get_file_info_recursive(d.save_path):
            mime = file_info.get('mime')
            extension = file_info.get('extension')
            file_type = guess_type(extension, mime)
            file_meta = {
                    'mime': mime,
                    'extension': extension,
                    'system_path': file_info.get('path'),
                    'parent_folder': file_info.get('parent'),
                    'file_type': file_type
                }
            file_meta.update(meta)

            episodeResources = list()
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
