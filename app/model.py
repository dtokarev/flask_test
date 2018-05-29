from app import db


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    value = db.Column(db.String(2000))


class QueueSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search = db.Column(db.String(250))
    error = db.Column(db.String(2000))


class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.String(120))
    download_rate_kb = db.Column(db.String(120))
    upload_rate_kb = db.Column(db.String(120))
    num_peers = db.Column(db.String(120))
    magnet_link = db.Column(db.String(1200))
    torrent_state = db.Column(db.String(120))
    created_at = db.Column(db.String(120))
    downloaded_at = db.Column(db.String(120))
    save_path = db.Column(db.String(120))
    status = db.Column(db.Integer, nullable=False)

    statuses = ["in_queue", "downloading", "finished", "updated", "error"]
    states = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']


class DownloadMetadata(db.Model):
    download_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    parsed_from_url = db.Column(db.String(120))
    length = db.Column(db.String(120))
    translation = db.Column(db.String(120))
    description = db.Column(db.String(120))
    year = db.Column(db.String(120))



