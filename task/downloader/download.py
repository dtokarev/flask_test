import os
import time
import threading
from datetime import datetime, timedelta

from sqlalchemy import func

from app_parser import db
from app_parser.domain.model import Download, Config
from app_parser.service.torrent_service import Torrent

download_pool_ids = set()


def run():
    while True:
        if not is_downloader_active() \
                or not is_space_enough() \
                or len(download_pool_ids) >= Config.get('BT_POOL_LIMIT', int):
            time.sleep(5)
            continue

        t = threading.Thread(target=download, daemon=True)
        t.start()
        print('new download thread started {}, pid {}'.format(t, os.getpid()))
        time.sleep(3)


def download():
    db.session.close()
    d = get_from_queue()

    if not d:
        print('no item to download')
        return

    try:
        download_pool_ids.add(d.id)

        d.save_path = os.path.join(Config.get('BT_DOWNLOAD_DIR'), str(int(d.search_id / 1000)), str(d.search_id))
        torrent = Torrent(d)
        torrent.download()
    except Exception as e:
        d.status = Download.STATUSES.ERROR
        d.error = str(e)
    finally:
        db.session.commit()
        download_pool_ids.remove(d.id)


def get_from_queue() -> Download:
    min_changed_at = datetime.utcnow() # - timedelta(minutes=30)
    return Download.query\
        .filter(
            Download.id.notin_(download_pool_ids) &
            (
                (Download.status.in_([Download.STATUSES.NEW, Download.STATUSES.PAUSED])) |
                ((Download.status == Download.STATUSES.DOWNLOADING) & (Download.changed_at < min_changed_at))
            )
        )\
        .order_by(func.rand())\
        .first()


def is_downloader_active():
    is_active = Config.get('BT_IS_ACTIVE', bool)
    if not is_active:
        print('Further downloads stopped via configs, downloads in queue {}'.format(len(download_pool_ids)))

    return is_active


def is_space_enough():
    from app_parser.utils.system import get_disk_usage_perc
    max = Config.get('BT_USE_DISK_SPACE_PERC', float)
    is_enough = get_disk_usage_perc() < max

    if not is_enough:
        print('Further downloads stopped disk space limit of {}% reached, downloads in queue {}'.format(max, len(download_pool_ids)))

    return is_enough


run()
