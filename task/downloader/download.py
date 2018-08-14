import os
import time
import multiprocessing as mp
from datetime import datetime, timedelta

from sqlalchemy import func

from app_parser import app, db
from app_parser.domain.model import Download, Config
from app_parser.service.torrent_service import Torrent
from app_parser.service import download_service


def run():
    download_service.forget_all()
    while True:
        if not is_downloader_active() \
                or not is_space_enough() \
                or download_service.count() >= Config.get('BT_POOL_LIMIT', int):
            time.sleep(10)
            continue

        d = get_from_queue()
        if not d:
            app.logger.warn('no item to download')
            time.sleep(10)
            continue

        fork = mp.Process(target=download, args=(d,), name='fork_download_id_{}'.format(d.id))
        fork.start()

        time.sleep(3)


def download(d: Download):
    app.logger.info('download_id {} - started pid {}'.format(d.id, os.getpid()))

    db.session.close()
    download_service.remember(d.id)
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
        download_service.forget(d)


def get_from_queue() -> Download:
    min_changed_at = datetime.utcnow() - timedelta(minutes=30)

    d = Download.query\
        .filter(
            Download.id.notin_(download_service.get_all())
            & (Download.status == Download.Statuses.DOWNLOADING) & (Download.changed_at < min_changed_at)
        )\
        .first()

    if not d:
        d = Download.query\
            .filter(
                Download.id.notin_(download_service.get_all())
                & (Download.status.in_([Download.Statuses.NEW, Download.Statuses.PAUSED]))
            )\
            .order_by(func.rand())\
            .first()

    return d


def is_downloader_active():
    is_active = Config.get('BT_IS_ACTIVE', bool)
    if not is_active:
        app.logger.warn('Further downloads stopped via configs, downloads in queue {}'
                        .format(download_service.count()) )

    return is_active


def is_space_enough():
    from app_parser.utils.system import get_disk_usage_perc
    max = Config.get('BT_USE_DISK_SPACE_PERC', float)
    current = get_disk_usage_perc()
    is_enough = current < max

    if not is_enough:
        app.logger.warn( 'Further downloads stopped disk space limit reached (limit={}%, used={}%), '
                         'downloads in queue {}'.format(max, current, download_service.count()) )

    return is_enough


run()
