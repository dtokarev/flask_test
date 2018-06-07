from app.domain.model import DownloadMeta, Download


class ParsedData:
    def __init__(self):
        self.raw_html = None
        self.raw_data = {}

        self.magnet_link = None
        self.title = None
        self.size = None

        self.country = None
        self.quality = None
        self.format = None
        self.duration = None
        self.translation = None
        self.subtitle = None
        self.subtitle_format = None
        self.gender = None
        self.description = None
        self.casting = None
        self.video_info = None
        self.audio_info = None

    def __repr__(self):
        return str(self.__dict__)

    def to_meta_model(self, model: DownloadMeta=None):
        if not model:
            model = DownloadMeta()

        model.raw_page_data = self.raw_data
        model.raw_page_html = self.raw_html
        model.country = self.country
        model.quality = self.quality
        model.format = self.format
        model.size = self.size
        model.duration = self.duration
        model.translation = self.translation
        model.subtitle = self.subtitle
        model.subtitle_format = self.subtitle_format
        model.gender = self.gender
        model.description = self.description
        model.casting = self.casting
        model.video_info = self.video_info
        model.audio_info = self.audio_info

        return model

    def to_download_model(self, model: Download=None):
        if not model:
            model = Download()

        model.magnet_link = self.magnet_link

        return model
