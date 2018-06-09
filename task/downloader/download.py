import os
import time
import threading
from datetime import datetime

import libtorrent as lt
from sqlalchemy import func

from app_parser import db
from app_parser.domain.model import Download


BT_POOL_LIMIT = 2

download_pool_ids = set()

ses = lt.session()
ses.listen_on(16000, 17000)
ses.start_dht()


def run():
    while True:
        time.sleep(10)
        if len(download_pool_ids) >= BT_POOL_LIMIT:
            continue

        t = threading.Thread(target=run_one)
        print('new thread started {}'.format(t))
        t.start()


def run_one():
    d = _get_from_queue()

    if not d:
        print('no item to download')
        return

    try:
        download_pool_ids.add(d.id)
        download(d)
    except Exception as e:
        d.error = str(e)
        d.status = Download.STATUSES.index('error')
        db.session.commit()
    finally:
        db.session.commit()
        download_pool_ids.remove(d.id)


def download(d: Download):
    path = os.path.join('/', 'tmp', 'd', str(int(d.search_id/1000)), str(d.search_id))

    params = {
        'save_path': path,
        'storage_mode': lt.storage_mode_t(2),
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True}
    handle = lt.add_magnet_uri(ses, d.magnet_link, params)
    d.save_path = path

    print('downloading metadata {}'.format(d.id))
    while not handle.has_metadata():
        bt_status = handle.status()
        update_download(d, bt_status)
        time.sleep(5)

    print('downloading {} to {}'.format(d.id, d.save_path))
    while handle.status().state != lt.torrent_status.seeding:
        bt_status = handle.status()
        d.status = Download.STATUSES.index('downloading')
        update_download(d, bt_status)
        time.sleep(5)

    d.status = Download.STATUSES.index('completed')
    d.downloaded_at = datetime.utcnow()
    update_download(d, handle.status())


def update_download(d: Download, bt_status: lt.torrent_status):
    d.bt_state = d.BT_STATES[bt_status.state] if bt_status else None
    d.progress = bt_status.progress * 100 if bt_status else 0
    d.download_rate_kb = bt_status.download_rate / 1000 if bt_status else 0
    d.upload_rate_kb = bt_status.upload_rate / 1000 if bt_status else 0
    d.num_peers = bt_status.num_peers if bt_status else 0
    d.total_download_kb = bt_status.total_download / 1000 if bt_status else 0
    db.session.commit()


def _get_from_queue() -> Download:
    return Download.query\
        .filter_by(status=Download.STATUSES.index('new'))\
        .filter(Download.id.notin_(download_pool_ids))\
        .order_by(func.rand())\
        .first()


run()