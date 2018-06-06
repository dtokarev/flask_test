from app.domain.search import Preferences, Matcher
from app.utils.unit_converter import *


def get_matcher(preferences: Preferences, actual_data: dict):
    matcher = Matcher()

    current_size = size_human_to_float(actual_data[Preferences.KEY_SIZE], GB)
    acceptable_size_lo = size_human_to_float(preferences.acceptable_size_range[0], GB)
    acceptable_size_hi = size_human_to_float(preferences.acceptable_size_range[1], GB)
    matcher.acceptable_size_matched = acceptable_size_lo < current_size < acceptable_size_hi

    return matcher
