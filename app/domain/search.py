from typing import List


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

        if best.get_quality() == 0 \
                or not best.acceptable_size_matched:
            raise Exception('best matcher did not meet any prerequisites (quality is 0) link {}'
                            .format(best.link))

        return best


class Preferences:
    KEY_SIZE = 'parsed_size'
    DEFAULT_UNIT = 'GB'

    # source_type_list = 'BDRip', 'HDTVRip'
    # genres_list = 'боевик', 'триллер', 'приключения', 'триллер', 'фантастика', 'мелодрама'

    def __init__(self, acceptable_size_range=('1.3 GB', '1.6 GB')):
        self.acceptable_size_range = acceptable_size_range
        # self.best_size_range = '700 MB', '800 MB'
        # self.source_type = None
        # self.genre = None
