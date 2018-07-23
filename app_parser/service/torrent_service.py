from datetime import datetime
import libtorrent as lt
import time

from app_parser.domain.model import Config, Download
from app_parser import db

ses = lt.session()
ses.listen_on(80, 80)
ses.start_dht()


class Torrent:
    def __init__(self, download: Download, configs=None):
        self.download = download
        self.bt_status = []
        if not configs:
            configs = {}

    def download(self):
        params = {
            'save_path': self.download.save_path,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True}
        handle = lt.add_magnet_uri(ses, self.download.magnet_link, params)

        status_calm_limit = Config.get('BT_CALM_TERM_LIMIT')
        status_calm_counter = status_calm_limit
        print('downloading metadata {}'.format(d.id))
        while not handle.has_metadata():
            self.bt_status = handle.status()
            time.sleep(5)

            status_calm_counter -= 1
            if status_calm_counter < 0:
                raise Exception('torrent status not changed {} times'.format(status_calm_limit))

        status_calm_counter = status_calm_limit
        print('downloading {} to {}'.format(self.download.id, self.download.save_path))
        while handle.status().state != lt.torrent_status.seeding:
            term_attr_before = self.download.download_rate_kb
            self.download.status = Download.STATUSES.index('downloading')
            self.update_download(handle.status())
            time.sleep(5)

            status_calm_counter = status_calm_counter - 1 if term_attr_before == d.download_rate_kb else status_calm_limit
            if status_calm_counter < 0:
                raise Exception('torrent status not changed {} times'.format(status_calm_limit))

        self.download.status = Download.STATUSES.index('completed')
        self.download.downloaded_at = datetime.utcnow()
        self.update_download(handle.status())

    def update_download(self, bt_status: lt.torrent_status):
        self.download.bt_state = self.download.BT_STATES[bt_status.state] if bt_status else None
        self.download.progress = bt_status.progress * 100 if bt_status else 0
        self.download.download_rate_kb = bt_status.download_rate / 1000 if bt_status else 0
        self.download.upload_rate_kb = bt_status.upload_rate / 1000 if bt_status else 0
        self.download.num_peers = bt_status.num_peers if bt_status else 0
        self.download.total_download_kb = bt_status.total_download / 1000 if bt_status else 0
        db.session.commit()