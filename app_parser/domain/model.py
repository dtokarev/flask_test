import json
import enum
from datetime import datetime
from typing import Union
from sqlalchemy.orm import validates

from app_parser import db


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    value = db.Column(db.String(2000))

    @staticmethod
    def get(key: str, vtype=str):
        record = Config.query.filter_by(name=key).first()
        if vtype == bool:
            return True if record.value.lower() in ['1', 'true', 'yes'] else False

        return vtype(record.value) if record else None


class ResourceType(enum.Enum):
    MOVIE = 'MOVIE'
    SERIES = 'SERIES'


class Search(db.Model):
    class STATUSES(enum.Enum):
        NEW = 'NEW'
        PROCESSING = 'PROCESSING'
        ERROR = 'ERROR'
        NOT_FOUND = 'NOT_FOUND'
        COMPLETED = 'COMPLETED'
        SEND = 'SEND'

    id = db.Column(db.BigInteger(), primary_key=True)
    title_ru = db.Column(db.String(250))
    title_en = db.Column(db.String(250))
    kinopoisk_id = db.Column(db.String(250), unique=True, nullable=True)
    error = db.Column(db.UnicodeText(4294000000))
    year = db.Column(db.SmallInteger, nullable=True)
    type = db.Column(db.Enum(ResourceType), index=True, nullable=False, default=ResourceType.MOVIE)
    status = db.Column(db.Enum(STATUSES), index=True, nullable=False, default=STATUSES.NEW)
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
    search_id = db.Column(db.BigInteger(), db.ForeignKey('search.id'), nullable=False)

    kinopoisk_id = db.Column(db.String(250))
    import_source_id = db.Column(db.String(250))

    page_link = db.Column(db.String(250))
    raw_page_data = db.Column(db.UnicodeText(4294000000))
    quality = db.Column(db.String(250))
    format = db.Column(db.String(250))
    country = db.Column(db.String(250))
    size = db.Column(db.String(250))
    title = db.Column(db.Text(65535))
    title_ru = db.Column(db.String(250))
    title_en = db.Column(db.String(250))
    duration = db.Column(db.Integer)
    translation = db.Column(db.String(250))
    subtitle = db.Column(db.String(250))
    subtitle_format = db.Column(db.String(250))
    gender = db.Column(db.Text(65535))
    description = db.Column(db.Text(65535))
    year = db.Column(db.Integer())
    casting = db.Column(db.Text(65535))
    video_info = db.Column(db.Text(65535))
    audio_info = db.Column(db.Text(65535))
    magnet_link = db.Column(db.Text(65535))

    @validates('quality', 'format', 'country', 'title', 'translation', 'subtitle',
               'subtitle_format', 'gender', 'description', 'casting', 'video_info', 'audio_info')
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value


class Download(db.Model):
    class STATUSES(enum.Enum):
        NEW = 'NEW'
        UPDATED = 'UPDATED'                 # торрент обновился, взять новые файлы
        DOWNLOADING = 'DOWNLOADING'
        PAUSED = 'PAUSED'
        COMPLETED = 'COMPLETED'
        ERROR = 'ERROR'

    BT_STATES = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']

    id = db.Column(db.BigInteger, primary_key=True)
    search_id = db.Column(db.BigInteger, db.ForeignKey('search.id'), nullable=False)
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
    status = db.Column(db.Enum(STATUSES))
    bt_state = db.Column(db.String(250))
    error = db.Column(db.UnicodeText(4294000000))


class Resource(db.Model):
    __bind_key__ = 'db_resource'
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
    __bind_key__ = 'db_resource'
    id = db.Column(db.BigInteger, primary_key=True)
    resource_id = db.Column(db.BigInteger, db.ForeignKey('resource.id'), nullable=False)
    type = db.Column(db.SmallInteger, index=True, nullable=False)
    mime = db.Column(db.String(250), nullable=False)
    domain = db.Column(db.String(250))
    system_path = db.Column(db.String(250))
    relative_path = db.Column(db.String(250))
