import os
import time

import libtorrent as lt
from sqlalchemy import func
from app.domain.model import Download


def run():
    d = _get_from_queue()

    if not d:
        print('no item to download')
        time.sleep(60)
        return

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

    print('downloading to {}'.format(path))
    print('downloading metadata {}...'.format(d.search_id))
    while not handle.has_metadata():
        time.sleep(1)
    print('got metadata, starting torrent download...')
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']
        print('{} complete (down: {} kb/s up: {} kB/s peers: {}) {} {}'.format(s.progress * 100,
                                                                               s.download_rate / 1000,
                                                                               s.upload_rate / 1000,
                                                                               s.num_peers,
                                                                               state_str[s.state],
                                                                               s.total_download / 1000000))
        time.sleep(5)


def _get_from_queue():
    return Download.query.filter_by(status=Download.statuses.index('new')).order_by(func.rand()).first()


run()