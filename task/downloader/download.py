import os
import time
import threading
from datetime import datetime, timedelta

from sqlalchemy import func

from app_parser import app
from app_parser import db
from app_parser.domain.model import Download, Config
from app_parser.service.torrent_service import Torrent

download_pool_ids = set()


def run():
    while True:
        db.session.close()
        if not is_downloader_active() \
                or not is_space_enough() \
                or len(download_pool_ids) >= Config.get('BT_POOL_LIMIT', int):
            time.sleep(5)
            continue

        d = get_from_queue()
        if not d:
            app.logger.warn('no item to download')
            time.sleep(10)
            continue

        t = threading.Thread(target=download, daemon=True, args=(d,), name='thread_download_id_{}'.format(d.id))
        t.start()
        app.logger.info('new download thread started {}, pid {}'.format(t, os.getpid()))
        time.sleep(3)


def download(d: Download):
    download_pool_ids.add(d.id)
    d = Download.query.filter_by(id=d.id).first()

    try:
        d.save_path = os.path.join(Config.get('BT_DOWNLOAD_DIR'), str(int(d.search_id / 1000)), str(d.search_id))
        torrent = Torrent(d)
        torrent.download()
    except Exception as e:
        d.status = Download.Statuses.ERROR
        d.error = str(e)
    finally:
        db.session.commit()
        download_pool_ids.remove(d.id)


def get_from_queue() -> Download:
    min_changed_at = datetime.utcnow() - timedelta(minutes=30)

    d = Download.query\
        .filter(
            Download.id.notin_(download_pool_ids)
            & (Download.status == Download.Statuses.DOWNLOADING) & (Download.changed_at < min_changed_at)
        )\
        .first()

    if not d:
        d = Download.query\
            .filter(
                Download.id.notin_(download_pool_ids)
                & (Download.status.in_([Download.Statuses.NEW, Download.Statuses.PAUSED]))
            )\
            .order_by(func.rand())\
            .first()

    return d


def is_downloader_active():
    is_active = Config.get('BT_IS_ACTIVE', bool)
    if not is_active:
        app.logger.warn('Further downloads stopped via configs, downloads in queue {}'.format(len(download_pool_ids)))

    return is_active


def is_space_enough():
    from app_parser.utils.system import get_disk_usage_perc
    max = Config.get('BT_USE_DISK_SPACE_PERC', float)
    current = get_disk_usage_perc()
    is_enough = current < max

    if not is_enough:
        app.logger.warn('Further downloads stopped disk space limit reached (limit={}%, used={}%), '
                        'downloads in queue {}'.format(max, current, len(download_pool_ids)))

    return is_enough


run()
