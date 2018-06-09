import os
import time
import threading
from datetime import datetime

import libtorrent as lt
from sqlalchemy import func

from app_parser import db
from app_parser.domain.model import Download


download_pool_ids = set()


def run():
    while True:
        d = _get_from_queue()

        if not d:
            print('no item to download')
            time.sleep(60)
            return

        while len(download_pool_ids) >= 2:
            print('download queue is full, waiting...')
            time.sleep(60)

        try:
            pass_to_download_pool(d)
            # t = threading.Thread(target=pass_to_download_pool, args={d: d})
            # print('new thread started {}'.format(t))
            # t.start()
        except Exception as e:
            d.error = str(e)
            d.status = Download.STATUSES[4]
            db.session.commit()
        finally:
            db.session.commit()
            download_pool_ids.remove(d.id)


def pass_to_download_pool(d: Download):
    download_pool_ids.add(d.id)
    print('ids in download pool {}'.format(str(download_pool_ids)))
    download(d)


def download(d: Download):
    path = os.path.join('/', 'tmp', 'd', str(int(d.search_id/1000)), str(d.search_id))
    ses = lt.session()
    ses.listen_on(6881, 6891)

    params = {
        'save_path': path,
        'storage_mode': lt.storage_mode_t(2),
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True}
    handle = lt.add_magnet_uri(ses, d.magnet_link, params)
    ses.start_dht()
    d.save_path = path

    while not handle.has_metadata():
        status = handle.status()
        print('downloading metadata id {}'.format(d.id))
        update_download(d, status)
        time.sleep(5)

    print('downloading {} to {}'.format(d.id, d.save_path))
    while handle.status().state != lt.torrent_status.seeding:
        status = handle.status()
        d.status = Download.STATUSES[1]
        update_download(d, status)
        time.sleep(5)

    d.downloaded_at = datetime.utcnow()


def update_download(d: Download, status: lt.torrent_status):
    d.bt_state = d.BT_STATES[status.state] if status else None
    d.progress = status.progress * 100 if status else 0
    d.download_rate_kb = status.download_rate / 1000 if status else 0
    d.upload_rate_kb = status.upload_rate / 1000 if status else 0
    d.num_peers = status.num_peers if status else 0
    d.total_download_kb = status.total_download / 1000000 if status else 0
    db.session.commit()


def _get_from_queue() -> Download:
    return Download.query\
        .filter_by(status=Download.STATUSES.index('new'))\
        .filter(Download.id.notin_(download_pool_ids))\
        .order_by(func.rand())\
        .first()


run()