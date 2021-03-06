from datetime import datetime
import libtorrent as lt
import time

from app_parser.domain.model import Config, Download
from app_parser import db

ses = lt.session()
ses.listen_on(80, 80)
ses.start_dht()


class Torrent:
    def __init__(self, d: Download):
        self.d = d
        self.bt_status = []
        params = {
            'save_path': self.d.save_path,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True}
        self.handle = lt.add_magnet_uri(ses, self.d.magnet_link, params)

    def download(self):
        status_calm_limit = Config.get('BT_CALM_TERM_LIMIT', int)
        status_calm_counter = status_calm_limit

        print('downloading metadata {}'.format(self.d.id))
        while not self.handle.has_metadata():
            self.bt_status = self.handle.status()
            time.sleep(5)

            status_calm_counter -= 1
            if status_calm_counter < 0:
                raise Exception('torrent status not changed {} times'.format(status_calm_limit))

        status_calm_counter = status_calm_limit
        print('downloading {} to {}'.format(self.d.id, self.d.save_path))
        while self.handle.status().state != lt.torrent_status.seeding:
            term_attr_before = self.d.download_rate_kb
            self.d.status = Download.Statuses.DOWNLOADING
            self.update_download(self.handle.status())
            time.sleep(5)

            status_calm_counter = status_calm_counter - 1 if term_attr_before == self.d.download_rate_kb else status_calm_limit
            if status_calm_counter < 0:
                raise Exception('torrent status not changed {} times'.format(status_calm_limit))

        self.d.status = Download.Statuses.COMPLETED
        self.d.downloaded_at = datetime.utcnow()
        self.update_download(self.handle.status())

    def update_download(self, bt_status: lt.torrent_status):
        self.d.bt_state = self.d.BT_STATES[bt_status.state] if bt_status else None
        self.d.progress = bt_status.progress * 100 if bt_status else 0
        self.d.download_rate_kb = bt_status.download_rate / 1000 if bt_status else 0
        self.d.upload_rate_kb = bt_status.upload_rate / 1000 if bt_status else 0
        self.d.num_peers = bt_status.num_peers if bt_status else 0
        self.d.total_download_kb = bt_status.total_download / 1000 if bt_status else 0

        db.session.commit()
