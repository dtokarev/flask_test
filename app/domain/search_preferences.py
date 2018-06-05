from typing import List

from app.utils.unit_converter import size_human_to_float, GB
from app.domain.const import ParserTokens


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
        """
        get first best matcher from list based on matcher's quality
        :param matchers:
        :return:
        """
        best = matchers[0]
        for matcher in matchers:
            if matcher.get_quality() > best.get_quality():
                best = matcher

        return best


class Preferences:
    # source_type_list = 'BDRip', 'HDTVRip'
    # genres_list = 'боевик', 'триллер', 'приключения', 'триллер', 'фантастика', 'мелодрама'

    def __init__(self, acceptable_size_range=('1.3 GB', '1.6 GB')):
        self.acceptable_size_range = acceptable_size_range
        # self.best_size_range = '700 MB', '800 MB'
        # self.source_type = None
        # self.genre = None

    def get_matcher(self, actual_data: dict) -> Matcher:
        matcher = Matcher()

        current_size = size_human_to_float(actual_data[ParserTokens.KEY_SIZE], GB)
        acceptable_size_lo = size_human_to_float(self.acceptable_size_range[0], GB)
        acceptable_size_hi = size_human_to_float(self.acceptable_size_range[1], GB)
        matcher.acceptable_size_matched = acceptable_size_lo < current_size < acceptable_size_hi

        return matcher


