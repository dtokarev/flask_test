from datetime import datetime

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
    parsed_page = db.Column(db.String(250))
    error = db.Column(db.Text())
    year = db.Column(db.SmallInteger, nullable=True)
    type = db.Column(db.SmallInteger, index=True, nullable=False, default=0)
    status = db.Column(db.SmallInteger, index=True, nullable=False, default=0)
    import_source = db.Column(db.String(250))
    extra_json = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    parsed_data = db.relationship("ParsedData", uselist=False, backref="search")
    download = db.relationship("Download", uselist=False, backref="search")

    types = ['movie', 'series']
    statuses = ['new', 'processing', 'completed', 'error', 'not found']


class ParsedData(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    search_id = db.Column(db.Integer(), db.ForeignKey('search.id'), nullable=False)

    kinopoisk_id = db.Column(db.String(250))
    mw_id = db.Column(db.String(250))

    raw_page_data = db.Column(db.Text())
    quality = db.Column(db.String(250))
    format = db.Column(db.String(250))
    size = db.Column(db.String(250))
    title_en = db.Column(db.String(250))
    title_ru = db.Column(db.String(250))
    duration = db.Column(db.Integer)
    translation = db.Column(db.String(250))
    subtitle = db.Column(db.String(250))
    subtitle_format = db.Column(db.String(250))
    gender = db.Column(db.String(250))
    description = db.Column(db.Text())
    year = db.Column(db.Integer())
    casting = db.Column(db.String(250))
    video_info = db.Column(db.String(250))
    audio_info = db.Column(db.String(250))


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
    created_at = db.Column(db.Date(), default=datetime.utcnow())
    downloaded_at = db.Column(db.Date())
    save_path = db.Column(db.String(250))
    status = db.Column(db.Integer, nullable=False)

    statuses = ["in_queue", "downloading", "finished", "updated", "error"]
    states = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']



