import enum
import json

from datetime import datetime

from sqlalchemy.orm import validates

from project import db
from project.domain.enum import ResourceType
from project.domain.search import Matcher


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

    @property
    def title(self):
        return self.title_ru if self.title_ru else self.title_en

    @property
    def season_number(self):
        default = 0
        if self.type == ResourceType.SERIES:
            return self.get_from_raw('season_number', default)

        return default

    def to_json(self):
        return {
            'id': self.id,
            'title_ru': self.title_ru,
            'kinopoisk_id': self.kinopoisk_id,
            'error': self.error,
            'status': self.status.value,
            'year': self.year,
        }

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


class ParsedData(db.Model):
    class DownloadStatuses(enum.Enum):
        NOT_SEND = 'NOT_SEND'
        SEND = 'SEND'
        DOWNLOADED = 'DOWNLOADED'

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
    download_status = db.Column(db.Enum(DownloadStatuses), index=True, nullable=False, default=DownloadStatuses.NOT_SEND)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    changed_at = db.Column(db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow, nullable=False)
    next_update_at = db.Column(db.DateTime, default=None, nullable=True)

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
    def create(s: Search, matcher: Matcher, parsed_data) -> 'ParsedData':
        parsed_data.page_link = matcher.link
        parsed_data.translation_code = matcher.translation
        parsed_data.search_id = s.id
        parsed_data.kinopoisk_id = s.kinopoisk_id
        parsed_data.title_en = s.title_en
        parsed_data.title_ru = s.title_ru
        parsed_data.import_source_id = s.import_source_id
        parsed_data.year = s.year

        return parsed_data