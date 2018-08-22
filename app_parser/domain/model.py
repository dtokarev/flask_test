import json
import enum
from datetime import datetime
from sqlalchemy.orm import validates

from app_parser import db, app
from app_parser.domain.Enum import FileTypes, ResourceType, ResourceStatuses
from app_parser.domain.search import Matcher


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    value = db.Column(db.String(2000))

    @staticmethod
    def get(key: str, vtype=str):
        record = db.session.query(Config).filter_by(name=key).first()
        if vtype == bool:
            return True if record.value.lower() in ['1', 'true', 'yes'] else False

        return vtype(record.value) if record else None


class Search(db.Model):
    class Statuses(enum.Enum):
        NEW = 'NEW'
        PROCESSING = 'PROCESSING'
        ERROR = 'ERROR'
        NOT_FOUND = 'NOT_FOUND'
        COMPLETED = 'COMPLETED'

    id = db.Column(db.BigInteger(), primary_key=True)
    title_ru = db.Column(db.String(250))
    title_en = db.Column(db.String(250))
    kinopoisk_id = db.Column(db.String(250), unique=True, nullable=True)
    error = db.Column(db.Text(16000000))
    year = db.Column(db.SmallInteger)
    type = db.Column(db.Enum(ResourceType), index=True, nullable=False, default=ResourceType.MOVIE)
    status = db.Column(db.Enum(Statuses), index=True, nullable=False, default=Statuses.NEW)
    import_source = db.Column(db.String(250))
    import_source_id = db.Column(db.String(250))
    raw = db.Column(db.Text(16000000))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    parsed_data = db.relationship("ParsedData", back_populates="search")
    # download = db.relationship("Download", back_populates="search")

    @staticmethod
    def create(movie: dict, source_name: str, r_type: ResourceType) -> 'Search':
        s = Search()
        s.title_ru = movie.get('title_ru')
        s.title_en = movie.get('title_en')
        s.kinopoisk_id = movie.get('kinopoisk_id')
        s.import_source = source_name
        s.import_source_id = movie.get('token')
        s.year = movie.get('year')
        s.type = r_type
        s.raw = json.dumps(movie, ensure_ascii=False)
        return s

    def get_from_raw(self, key: str, default=None) -> str:
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
    kinopoisk_id = db.Column(db.String(250))
    import_source_id = db.Column(db.String(250))
    page_link = db.Column(db.String(250))
    raw_page_data = db.Column(db.Text(16000000))
    quality = db.Column(db.String(250))
    format = db.Column(db.String(250))
    country = db.Column(db.String(250))
    size = db.Column(db.String(250))
    title = db.Column(db.Text(65535))
    title_ru = db.Column(db.String(250))
    title_en = db.Column(db.String(250))
    duration = db.Column(db.Integer)
    translation = db.Column(db.String(250))
    translation_code = db.Column(db.String(250))
    subtitle = db.Column(db.String(250))
    subtitle_format = db.Column(db.String(250))
    genre = db.Column(db.Text(65535))
    description = db.Column(db.Text(65535))
    year = db.Column(db.Integer())
    casting = db.Column(db.Text(65535))
    video_info = db.Column(db.Text(65535))
    audio_info = db.Column(db.Text(65535))
    magnet_link = db.Column(db.Text(65535))

    search_id = db.Column(db.BigInteger(), db.ForeignKey('search.id'), nullable=False)
    search = db.relationship("Search", back_populates="parsed_data")

    @validates('quality', 'format', 'country', 'title', 'translation', 'subtitle',
               'subtitle_format', 'gender', 'description', 'casting', 'video_info', 'audio_info')
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value

    @staticmethod
    def create(s: Search, matcher: Matcher, raw_html) -> 'ParsedData':
        from app_parser.scrapper import Rutracker
        parsed_data = Rutracker.parse_html(raw_html)
        parsed_data.page_link = matcher.link
        parsed_data.translation_code = matcher.translation
        parsed_data.search_id = s.id
        parsed_data.kinopoisk_id = s.kinopoisk_id
        parsed_data.title_en = s.title_en
        parsed_data.title_ru = s.title_ru
        parsed_data.import_source_id = s.import_source_id
        parsed_data.year = s.year

        return parsed_data


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
    progress = db.Column(db.Float(), default=0)
    download_rate_kb = db.Column(db.Float())
    upload_rate_kb = db.Column(db.Float())
    total_download_kb = db.Column(db.Float())
    num_peers = db.Column(db.Integer())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    changed_at = db.Column(db.DateTime(), onupdate=datetime.utcnow)
    next_update_at = db.Column(db.DateTime(), nullable=True, default=None)
    downloaded_at = db.Column(db.DateTime())
    save_path = db.Column(db.String(250))
    status = db.Column(db.Enum(Statuses))
    bt_state = db.Column(db.String(250))
    error = db.Column(db.Text(16000000))
    files = db.Column(db.Text(16000000))
    type = db.Column(db.Enum(ResourceType), index=True, nullable=False, default=ResourceType.MOVIE)

    parsed_data_id = db.Column(db.BigInteger(), db.ForeignKey('parsed_data.id'), nullable=False)
    parsed_data = db.relationship("ParsedData", uselist=False)

    @staticmethod
    def create(data: ParsedData, resource_type: ResourceType) -> 'Download':
        download = Download()
        download.parsed_data = data
        download.progress = 0
        download.status = Download.Statuses.NEW
        download.type = resource_type

        return download


class Episode(db.Model):
    __bind_key__ = 'db_resource'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    episode_no = db.Column(db.Integer())
    episode_title = db.Column(db.Text(), nullable=False)
    season_no = db.Column(db.Integer(), default=0)
    kinopoisk_id = db.Column(db.String(250))
    translation = db.Column(db.Text(65535))
    description = db.Column(db.Text(65535))
    year = db.Column(db.Integer())
    duration = db.Column(db.Integer())
    genre = db.Column(db.Text(65535))
    country = db.Column(db.Text())
    status = db.Column(db.Enum(ResourceStatuses))
    type = db.Column(db.Enum(ResourceType), index=True, nullable=False, default=ResourceType.MOVIE)
    mime = db.Column(db.String(250), nullable=False)
    extension = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=True)
    system_path = db.Column(db.String(250))
    parent_folder = db.Column(db.String(250))

    parsed_data_id = db.Column(db.BigInteger(), nullable=False)

    @staticmethod
    def create(params: dict):
        media = Episode()
        media.status = Episode.Statuses.NOT_ENCODED
        media.type = params.get('type')
        media.parsed_data_id = params.get('parsed_data_id')

        media.mime = params.get('mime')
        media.extension = params.get('extension')
        media.system_path = params.get('system_path')
        media.parent_folder = params.get('parent_folder')

        media.kinopoisk_id = params.get('kinopoisk_id')
        media.episode_title = params.get('episode_title')
        media.year = params.get('year')
        media.episode_no = params.get('episode_no') if media.type is ResourceType.SERIES else None
        media.genre = params.get('genre')
        media.country = params.get('country')
        media.description = params.get('description')
        media.duration = params.get('duration')
        media.translation = params.get('translation')

        return media


class EpisodeResource(db.Model):
    __bind_key__ = 'db_resource'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    file_type = db.Column(db.Enum(FileTypes))
    status = db.Column(db.Enum(ResourceStatuses))
    mime = db.Column(db.String(250), nullable=False)
    extension = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=True)
    system_path = db.Column(db.String(250))
    parent_folder = db.Column(db.String(250))

    episode_id = db.Column(db.BigInteger(), db.ForeignKey('episode.id'), nullable=False)
    episode = db.relationship("Episode", uselist=False)

    @staticmethod
    def create(params: dict):
        resource = EpisodeResource()
        resource.status = Episode.Statuses.NOT_ENCODED
        resource.file_type = params.get('file_type')

        resource.mime = params.get('mime')
        resource.extension = params.get('extension')
        resource.system_path = params.get('system_path')
        resource.parent_folder = params.get('parent_folder')

        return resource
