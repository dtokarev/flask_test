from typing import List

from app_parser.domain.Enum import ResourceType
from app_parser.exception import ResultNotFoundException


class Matcher:
    """
    Container for matches between search result and SearchPreferences.
    Some matchers must match to make result valid, other matchers increase overall quality of result
    """
    def __init__(self):
        self.link = ''
        # self.best_size_matched = False
        self.acceptable_size_matched = False
        self.min_seeders_matched = False
        self.keyword_matched = False
        self.seeders_num = 0
        self.category_matched = False
        self.translation = ''
        # self.source_type_matched = False
        # self.genre_matched = False

    def __repr__(self):
        return str(vars(self))

    def get_quality(self) -> int:
        """
        Overall quality of the matcher
        """
        quality = 0

        if not self.acceptable_size_matched \
                or not self.min_seeders_matched\
                or not self.keyword_matched\
                or not self.category_matched:
            return quality

        quality += 10                   # at least must prerequisites matched
        quality += self.seeders_num

        return quality

    def bind_link(self, link: str):
        self.link = link

    @staticmethod
    def get_best(matchers: List['Matcher'], cnt=1) -> List['Matcher']:
        """
        get best matcher from list based on matcher's quality
        """
        if not matchers:
            raise ResultNotFoundException('No match found')

        matchers = sorted(matchers, key=lambda m: -m.get_quality())
        used_translations = set()
        best = list()

        for i in range(cnt):
            for m in matchers:
                translation = m.translation.upper()
                if m.get_quality() > 0 and translation not in used_translations:
                    used_translations.add(translation)
                    best.append(m)
                    break

        if not best:
            raise ResultNotFoundException('No good match found {}'.format(matchers))

        return best


class SearchPreferences:
    """
    Definitions of preferred and obligatory params in search results
    """
    KEY_SIZE = 'parsed_size'
    KEY_SEEDERS = 'parsed_seeders'
    KEY_KEYWORD = 'parsed_keyword'
    KEY_CATEGORY_NAME = 'parsed_category_name'
    KEY_TRANSLATION = 'parsed_transaltion'
    DEFAULT_UNIT = 'GB'

    # source_type_list = 'BDRip', 'HDTVRip'
    # genres_list = 'боевик', 'триллер', 'приключения', 'триллер', 'фантастика', 'мелодрама'

    def __init__(self,
                 keywords: List, year: int = None,
                 acceptable_size_range=('700 MB', '2.5 GB'),
                 sample_count=1
                 ):
        # TODO: inject params from outside

        from app_parser.utils.search import generate_keywords

        self.acceptable_size_range = acceptable_size_range
        self.min_seeders = 2
        self.keywords = keywords
        self.generated_keywords = generate_keywords(*keywords, year=year)
        self.category_names_like = ('Фильм', 'Сериал', 'Кино', 'Видео', 'Кинематограф')
        self.sample_count = sample_count
        # self.best_size_range = '700 MB', '800 MB'
        # self.source_type = None
        # self.genre = None

    @staticmethod
    def get_default_sample_count_for_type(t: ResourceType):
        return 4 if t == ResourceType.SERIES else 2

    def __repr__(self, *args, **kwargs):
        return str(self.__dict__)
