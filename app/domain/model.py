import json
from datetime import datetime
from typing import Union

from app import db


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    value = db.Column(db.String(2000))

    @staticmethod
    def get(key: str) -> str:
        record = Config.query.filter_by(name=key).first()
        return record.value if record else None


class Search(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    title_ru = db.Column(db.String(250))
    title_en = db.Column(db.String(250))
    kinopoisk_id = db.Column(db.String(250), unique=True, nullable=True)
    page_link = db.Column(db.String(250))
    error = db.Column(db.UnicodeText(4294000000))
    year = db.Column(db.SmallInteger, nullable=True)
    type = db.Column(db.SmallInteger, index=True, nullable=False, default=0)
    status = db.Column(db.SmallInteger, index=True, nullable=False, default=0)
    import_source = db.Column(db.String(250))
    import_source_id = db.Column(db.String(250))
    raw = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    parsed_data = db.relationship("DownloadMeta", uselist=False, backref="search")
    download = db.relationship("Download", uselist=False, backref="search")

    types = ['movie', 'series']
    statuses = ['new', 'processing', 'completed', 'error', 'not found']

    def get_from_raw(self, key: str) -> Union[str, None]:
        try:
            d = json.loads(self.raw)
            return d.get(key, None)
        except ValueError:
            return None


class DownloadMeta(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    search_id = db.Column(db.Integer(), db.ForeignKey('search.id'), nullable=False)

    kinopoisk_id = db.Column(db.String(250))
    import_source_id = db.Column(db.String(250))

    raw_page_data = db.Column(db.UnicodeText(4294000000))
    raw_page_html = db.Column(db.UnicodeText(4294000000))
    quality = db.Column(db.String(250))
    format = db.Column(db.String(250))
    country = db.Column(db.String(250))
    size = db.Column(db.String(250))
    title_en = db.Column(db.Text())
    title_ru = db.Column(db.Text())
    duration = db.Column(db.Integer)
    translation = db.Column(db.String(250))
    subtitle = db.Column(db.String(250))
    subtitle_format = db.Column(db.String(250))
    gender = db.Column(db.Text())
    description = db.Column(db.Text())
    year = db.Column(db.Integer())
    casting = db.Column(db.Text())
    video_info = db.Column(db.Text())
    audio_info = db.Column(db.Text())


class Download(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'), nullable=False)
#     type = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.Float())
    download_rate_kb = db.Column(db.Float())
    upload_rate_kb = db.Column(db.Float())
    num_peers = db.Column(db.Integer())
    magnet_link = db.Column(db.Text())
    torrent_state = db.Column(db.String(250))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    downloaded_at = db.Column(db.DateTime())
    save_path = db.Column(db.String(250))
    status = db.Column(db.Integer, nullable=False)

    statuses = ["new", "downloading", "finished", "updated", "error"]
    states = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']


class Resource(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    type = db.Column(db.SmallInteger, index=True, nullable=False)
    domain = db.Column(db.String(250), nullable=False)
    uri = db.Column(db.String(250), nullable=False)
    system_path = db.Column(db.String(250), nullable=False)
    episode_no = db.Column(db.Integer())
    episode_title = db.Column(db.UnicodeText(), nullable=False)
    season_no = db.Column(db.Integer())
    season_title = db.Column(db.UnicodeText())
    resource_media = db.relationship("ResourceMedia", uselist=False, backref="resource")


class ResourceMedia(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    resource_id = db.Column(db.BigInteger, db.ForeignKey('resource.id'), nullable=False)
    type = db.Column(db.SmallInteger, index=True, nullable=False)
    mime = db.Column(db.String(250), nullable=False)
    domain = db.Column(db.String(250))
    system_path = db.Column(db.String(250))
    relative_path = db.Column(db.String(250))
