from typing import List

from app.utils.unit_converter import parse_size, GB

KEY_SIZE = 'size'


class Matcher:
    def __init__(self):
        self.link = ''
        # self.best_size_matched = False
        self.acceptable_size_matched = False
        # self.source_type_matched = False
        # self.genre_matched = False

    def get_quality(self):
        quality = 0
        if self.acceptable_size_matched:
            quality += 10

        return quality

    def bind_link(self, link: str):
        self.link = link

    @staticmethod
    def get_best(matchers: List['Matcher']):
        best = matchers[0]
        for matcher in matchers:
            if matcher.get_quality() > best.get_quality():
                best = matcher

        return best


class Preferences:
    source_type_list = 'BDRip', 'HDTVRip'
    genres_list = 'боевик', 'триллер', 'приключения', 'триллер', 'фантастика', 'мелодрама'

    def __init__(self):
        # self.best_size_range = '700 MB', '800 MB'
        self.acceptable_size_range = '1.4 GB', '1.5 GB'
        # self.source_type = None
        # self.genre = None

    def get_matcher(self, result_data: dict) -> Matcher:
        matcher = Matcher()

        current_size = parse_size(result_data[KEY_SIZE], GB)
        best_size_lo = parse_size(self.acceptable_size_range[0], GB)
        best_size_hi = parse_size(self.acceptable_size_range[1], GB)
        matcher.best_size_matched = best_size_lo < current_size < best_size_hi

        return matcher


