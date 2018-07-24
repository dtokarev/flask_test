from typing import List

from app_parser.exception import ResultNotFoundException
from app_parser.utils.search import generate_keywords


class Matcher:
    def __init__(self):
        self.link = ''
        # self.best_size_matched = False
        self.acceptable_size_matched = False
        self.min_seeders_matched = False
        self.keyword_matched = False
        self.seeders_num = 0
        # self.source_type_matched = False
        # self.genre_matched = False

    def __repr__(self):
        return str(self.__dict__)

    def get_quality(self):
        quality = 0

        if not self.acceptable_size_matched \
                or not self.min_seeders_matched\
                or not self.keyword_matched:
            return quality

        quality += 10                   # at least must prerequisites matched
        quality += self.seeders_num

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
        if not matchers:
            raise ResultNotFoundException('matcher - no result')

        best = sorted(matchers, key=lambda m: m.get_quality())[-1]

        if best.get_quality() == 0:
            print(matchers)
            raise ResultNotFoundException('matcher - best quality is 0 link {}'.format(best.link))

        return best


class SearchPreferences:
    KEY_SIZE = 'parsed_size'
    KEY_SEEDERS = 'parsed_seeders'
    KEY_KEYWORD = 'parsed_keyword'
    DEFAULT_UNIT = 'GB'

    # source_type_list = 'BDRip', 'HDTVRip'
    # genres_list = 'боевик', 'триллер', 'приключения', 'триллер', 'фантастика', 'мелодрама'

    def __init__(self, keywords: List, year: int = None, acceptable_size_range=('700 MB', '1.6 GB')):
        self.acceptable_size_range = acceptable_size_range
        self.min_seeders = 2
        self.keywords = keywords
        self.generated_keywords = generate_keywords(*keywords, year=year)
        # self.best_size_range = '700 MB', '800 MB'
        # self.source_type = None
        # self.genre = None

    def __repr__(self, *args, **kwargs):
        return str(self.__dict__)
