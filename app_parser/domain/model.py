import json
import enum
from datetime import datetime
from typing import Union
from sqlalchemy.orm import validates

from app_parser import db, app


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    value = db.Column(db.String(2000))

    @staticmethod
    def get(key: str, vtype=str):
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy(app)
        record = db.session.query(Config).filter_by(name=key).first()
        db.session.remove()
        if vtype == bool:
            return True if record.value.lower() in ['1', 'true', 'yes'] else False

        return vtype(record.value) if record else None


class ResourceType(enum.Enum):
    MOVIE = 'MOVIE'
    SERIES = 'SERIES'


class Search(db.Model):
    class Statuses(enum.Enum):
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
    status = db.Column(db.Enum(Statuses), index=True, nullable=False, default=Statuses.NEW)
    import_source = db.Column(db.String(250))
    import_source_id = db.Column(db.String(250))
    raw = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    parsed_data = db.relationship("ParsedData", uselist=False, backref="search")
    download = db.relationship("Download", uselist=False, backref="search")

    def get_from_raw(self, key: str, default = None) -> str:
        try:
            d = json.loads(self.raw)
            return d.get(key, default)
        except ValueError:
            return default

    @property
    def title(self):
        return self.title_ru if self.title_ru else self.title_en

    @property
    def season_number(self):
        default = 0
        if self.type == ResourceType.SERIES:
            return self.get_from_raw('season_number', default)

        return default


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
    class Statuses(enum.Enum):
        NEW = 'NEW'
        UPDATED = 'UPDATED'                 # торрент обновился, взять новые файлы
        DOWNLOADING = 'DOWNLOADING'
        PAUSED = 'PAUSED'
        COMPLETED = 'COMPLETED'
        ERROR = 'ERROR'
        DECOMPOSED = 'DECOMPOSED'

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
    status = db.Column(db.Enum(Statuses))
    bt_state = db.Column(db.String(250))
    error = db.Column(db.UnicodeText(4294000000))


class Resource(db.Model):
    __bind_key__ = 'db_resource'
    id = db.Column(db.BigInteger, primary_key=True)
    search_id = db.Column(db.BigInteger, nullable=True)
    type = db.Column(db.Enum(ResourceType), index=True, nullable=False, default=ResourceType.MOVIE)
    system_path = db.Column(db.String(250), nullable=False)
    season_no = db.Column(db.Integer())
    season_title = db.Column(db.UnicodeText())
    json_meta = db.Column(db.UnicodeText(4294000000))
    resource_media = db.relationship("ResourceMedia", uselist=False, backref="resource")

    @staticmethod
    def create(params: dict):
        r = Resource()
        r.search_id = params.get('search_id')
        r.type = params.get('type')
        r.system_path = params.get('system_path')
        r.season_title = params.get('season_title')
        r.season_no = params.get('season_no')
        r.json_meta = params.get('json_meta')
        return r


class ResourceMedia(db.Model):
    ext_videos = {'avi', 'mp4', 'webm', 'mkv', 'mov', 'wmv', 'mpeg'}
    ext_audio = {'mp3'}
    ext_subs = {'srt', 'sami'}

    class Statuses(enum.Enum):
        NOT_ENCODED = 'NOT_ENCODED'
        ENCODING = 'ENCODING'
        NOT_DEPLOYED = 'NOT_DEPLOYED'
        READY = 'READY'

    class Types(enum.Enum):
        VIDEO = 'VIDEO'
        SUBTITLE = 'SUBTITLE'
        AUDIO = 'AUDIO'

    __bind_key__ = 'db_resource'
    id = db.Column(db.BigInteger, primary_key=True)
    resource_id = db.Column(db.BigInteger, db.ForeignKey('resource.id'), nullable=False)
    episode_no = db.Column(db.Integer())
    episode_title = db.Column(db.UnicodeText(), nullable=False)
    type = db.Column(db.Enum(Types), index=True, nullable=False)
    mime = db.Column(db.String(250), nullable=False)
    extension = db.Column(db.String(250), nullable=False)
    status = db.Column(db.Enum(Statuses))
    url = db.Column(db.String(250), nullable=True)
    system_path = db.Column(db.String(250))
    parent_folder = db.Column(db.String(250))

    @staticmethod
    def create(r: Resource, params: dict):
        media = ResourceMedia()
        media.resource_id = r.id
        media.mime = params.get('mime')
        media.extension = params.get('extension')
        media.system_path = params.get('path')
        media.type = media.guess_type()
        media.parent_folder = params.get('parent_folder')

        if r.type == ResourceType.MOVIE:
            media.episode_no = 0
            media.episode_title = r.season_title
        else:
            pass

        if media.type == ResourceMedia.Types.VIDEO:
            media.status = ResourceMedia.Statuses.NOT_ENCODED
        else:
            media.status = ResourceMedia.Statuses.NOT_DEPLOYED

        return media

    def guess_type(self):
        if not self.extension or not self.mime:
            raise Exception('fill extension and mime first, before guessing file type')
        if 'video' in self.mime.lower() or self.extension in self.ext_videos:
            return ResourceMedia.Types.VIDEO
        elif self.extension in self.ext_subs:
            return ResourceMedia.Types.SUBTITLE
        elif 'audio' in self.mime.lower() or self.extension in self.ext_videos:
            return ResourceMedia.Types.AUDIO

    def is_junk(self):
        return not self.guess_type()
