from typing import List

from .enum import ResourceType
from .exception import ResultNotFoundException


class Matcher:
    """
    Container for matches between search result and SearchPreferences.
    Some properties must match exactly to make result valid, others increase overall quality of result
    """
    def __init__(self):
        self.link = ''
        self.acceptable_size_matched = False
        self.min_seeders_matched = False
        self.keyword_matched = False
        self.seeders_num = 0
        self.category_matched = False
        self.translation = ''

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
    def get_best(matches: List['Matcher'], cnt=1) -> List['Matcher']:
        """
        get best matcher from list based on matcher's quality
        """
        if not matches:
            raise ResultNotFoundException('No match found')

        matches = sorted(matches, key=lambda m: -m.get_quality())
        used_translations = set()
        best = list()

        for i in range(cnt):
            for m in matches:
                translation = m.translation.upper()
                if m.get_quality() > 0 and translation not in used_translations:
                    used_translations.add(translation)
                    best.append(m)
                    break

        if not best:
            raise ResultNotFoundException('No good match found {}'.format(matches))

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

    def __init__(self,
                 keywords: List, year: int = None,
                 acceptable_size_range=('700 MB', '2.5 GB'),
                 sample_count=1
                 ):
        """
        :param keywords: generated keywords
        :param year:
        :param acceptable_size_range: tuple of 2 elements in human format
        :type sample_count: object
        """
        from project.utils.search import generate_keywords

        self.acceptable_size_range = acceptable_size_range
        self.min_seeders = 2
        self.keywords = keywords
        self.generated_keywords = generate_keywords(*keywords, year=year)
        self.category_names_like = ('Фильм', 'Сериал', 'Кино', 'Видео', 'Кинематограф')
        self.sample_count = sample_count

    @staticmethod
    def get_default_sample_count_for_type(t: ResourceType):
        return 4 if t == ResourceType.SERIES else 2

    def __repr__(self, *args, **kwargs):
        return str(self.__dict__)
