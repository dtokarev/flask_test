from time import sleep

from app_parser import db
from app_parser.domain.model import Download, Resource, ResourceMedia
from app_parser.utils.system import get_file_info_recursive


def run():
    while True:
        d = get_from_queue()
        if not d:
            print('no completed downloads')
            sleep(20)
            continue

        search = d.search
        parsed = search.parsed_data

        resource = Resource.query.filter_by(search_id=search.id).first()
        if not resource:
            resource = Resource.create({
                'search_id': search.id,
                'type': search.type,
                'system_path': d.save_path,
                'season_title': search.title,
                'season_no': search.season_number,
            })
            db.session.add(resource)
            db.session.commit()

        for file_info in get_file_info_recursive(d.save_path):
            media = ResourceMedia.create(resource, {
                'mime': file_info.get('mime'),
                'extension': file_info.get('extension'),
                'path': file_info.get('path'),
            })

            if not media.is_junk():
                db.session.add(media)

        d.status = Download.Statuses.DECOMPOSED
        db.session.commit()


def get_from_queue() -> Download:
    return Download.query.filter_by(status=Download.Statuses.COMPLETED).first()

run()
