import json
import enum
from datetime import datetime
from typing import Union

from app_parser import db


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    value = db.Column(db.String(2000))

    @staticmethod
    def get(key: str) -> str:
        record = Config.query.filter_by(name=key).first()
        return record.value if record else None


class ParsingStatus(enum.Enum):
    NEW = 'new'
    PROCESSING = 'processing'
    ERROR = 'error'
    NOT_FOUND = 'not found'
    COMPLETED = 'completed'
    SEND = 'send'


class ResourceType(enum.Enum):
    MOVIE = 'movie'
    SERIES = 'series'


class Search(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    title_ru = db.Column(db.String(250))
    title_en = db.Column(db.String(250))
    kinopoisk_id = db.Column(db.String(250), unique=True, nullable=True)
    error = db.Column(db.UnicodeText(4294000000))
    year = db.Column(db.SmallInteger, nullable=True)
    type = db.Column(db.Enum(ResourceType), index=True, nullable=False, default=ResourceType.MOVIE)
    status = db.Column(db.Enum(ParsingStatus), index=True, nullable=False, default=ParsingStatus.NEW)
    import_source = db.Column(db.String(250))
    import_source_id = db.Column(db.String(250))
    raw = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    parsed_data = db.relationship("ParsedData", uselist=False, backref="search")
    download = db.relationship("Download", uselist=False, backref="search")

    def get_from_raw(self, key: str) -> Union[str, None]:
        try:
            d = json.loads(self.raw)
            return d.get(key, None)
        except ValueError:
            return None


class ParsedData(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    search_id = db.Column(db.Integer(), db.ForeignKey('search.id'), nullable=False)

    kinopoisk_id = db.Column(db.String(250))
    import_source_id = db.Column(db.String(250))

    page_link = db.Column(db.String(250))
    raw_page_data = db.Column(db.UnicodeText(4294000000))
    raw_page_html = db.Column(db.UnicodeText(4294000000))
    quality = db.Column(db.String(250))
    format = db.Column(db.String(250))
    country = db.Column(db.String(250))
    size = db.Column(db.String(250))
    title = db.Column(db.Text())
    title_ru = db.Column(db.String(250))
    title_en = db.Column(db.String(250))
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
    magnet_link = db.Column(db.Text())


class Download(db.Model):
    STATUSES = ["new", "downloading", "finished", "updated", "error"]
    BT_STATES = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']

    id = db.Column(db.BigInteger, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'), nullable=False)
    # type = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.Float(), default=0)
    download_rate_kb = db.Column(db.Float())
    upload_rate_kb = db.Column(db.Float())
    total_download_kb = db.Column(db.Float())
    num_peers = db.Column(db.Integer())
    magnet_link = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    changed_at = db.Column(db.DateTime(), onupdate=datetime.utcnow)
    downloaded_at = db.Column(db.DateTime())
    save_path = db.Column(db.String(250))
    status = db.Column(db.String(250))
    bt_state = db.Column(db.String(250))
    error = db.Column(db.UnicodeText(4294000000))


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
