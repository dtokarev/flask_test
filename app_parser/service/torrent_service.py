from datetime import datetime
import time
from typing import Optional

import libtorrent as lt

from app_parser.domain.model import Config, Download
from app_parser import db, app

BYTES_IN_MB = 10**6
ses = lt.session()
ses.listen_on(80, 80)
ses.set_settings({
    # Setting the value to -1 means unlimited.
    'active_downloads': -1,
    # The target number of active torrents is min(active_downloads + active_seeds, active_limit)
    'active_limit': -1,
    # upload_rate_limit and download_rate_limit sets the session-global limits of upload and download rate limits,
    # in bytes per second. By default peers on the local network are not rate limited.
    'download_rate_limit': 40 * BYTES_IN_MB,
    'upload_rate_limit': 40 * BYTES_IN_MB,
})
ses.start_dht()
ses.set_max_connections(10000)


class Torrent:
    def __init__(self, d: Download):
        self.d = d
        self.bt_status = []

        params = {
            'save_path': self.d.save_path,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True,
            # 'trackers': [
            #     'http://bt1.t-ru.org/ann'
            #     'http://bt2.t-ru.org/ann'
            #     'http://bt3.t-ru.org/ann'
            #     'http://bt4.t-ru.org/ann'
            # ],
        }
        self.torrent_handle = lt.add_magnet_uri(ses, self.d.magnet_link, params)

    def download(self):
        status_calm_limit = Config.get('BT_CALM_TERM_LIMIT', int)
        status_calm_counter = status_calm_limit

        app.logger.info('downloading metadata {}'.format(self.d.id))
        while not self.torrent_handle.has_metadata():
            self.bt_status = self.torrent_handle.status()
            time.sleep(5)

            status_calm_counter -= 1
            if status_calm_counter < 0:
                raise Exception('torrent status not changed {} times'.format(status_calm_limit))

        status_calm_counter = status_calm_limit
        app.logger.info('downloading {} to {}'.format(self.d.id, self.d.save_path))
        while not self.torrent_handle.is_seed():
            term_attr_before = self.d.download_rate_kb
            self.d.status = Download.Statuses.DOWNLOADING
            self.update_download(self.torrent_handle.status())
            time.sleep(5)

            status_calm_counter = status_calm_counter - 1 if term_attr_before == self.d.download_rate_kb else status_calm_limit
            if status_calm_counter < 0:
                raise Exception('torrent status not changed {} times'.format(status_calm_limit))

        self.d.status = Download.Statuses.COMPLETED
        self.d.downloaded_at = datetime.utcnow()
        self.update_download(None)

    def update_download(self, bt_status: Optional[lt.torrent_status]):
        self.d.bt_state = self.d.BT_STATES[bt_status.state] if bt_status else 'finished'
        self.d.progress = bt_status.progress * 100 if bt_status else 0
        self.d.download_rate_kb = bt_status.download_rate / 1000 if bt_status else 0
        self.d.upload_rate_kb = bt_status.upload_rate / 1000 if bt_status else 0
        self.d.num_peers = bt_status.num_peers if bt_status else 0
        self.d.total_download_kb = bt_status.total_download / 1000 if bt_status else 0

        if bt_status and bt_status.error:
            self.d.error = bt_status.error

        db.session.commit()
