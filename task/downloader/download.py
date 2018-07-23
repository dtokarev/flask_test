import os
import time
import threading

from sqlalchemy import func

from app_parser import db
from app_parser.domain.model import Download, Config
from app_parser.service.bt import Torrent

download_pool_ids = set()


def run():
    while True:
        if not _is_downloader_active():
            time.sleep(5)
            continue

        time.sleep(1)
        if len(download_pool_ids) >= Config.get('BT_POOL_LIMIT', int):
            continue

        t = threading.Thread(target=download)
        t.daemon = True
        t.start()
        print('new download thread started {}'.format(t))


def download():
    d = _get_from_queue()

    if not d:
        print('no item to download')
        time.sleep(60)
        return

    try:
        download_pool_ids.add(d.id)
        d.save_path = os.path.join(Config.get('BT_DOWNLOAD_DIR'), str(int(d.search_id / 1000)), str(d.search_id))
        torrent = Torrent(d)
        torrent.download()
    except Exception as e:
        d.error = str(e)
        d.status = Download.STATUSES.ERROR
    finally:
        db.session.commit()
        download_pool_ids.remove(d.id)


def _get_from_queue() -> Download:
    return Download.query\
        .filter_by(status=Download.STATUSES.NEW)\
        .filter(Download.id.notin_(download_pool_ids))\
        .order_by(func.rand())\
        .first()


def _is_downloader_active():
    is_active = Config.get('BT_IS_ACTIVE', bool)
    if not is_active:
        print('Further downloads stopped via configs, downloads in queue {}'.format(len(download_pool_ids)))

    return is_active


run()
