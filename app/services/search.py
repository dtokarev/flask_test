from app.domain.search import Preferences, Matcher
from app.utils.unit_converter import size_human_to_float


def get_matcher(preferences: Preferences, actual_data: dict):
    matcher = Matcher()
    size_unit = Preferences.DEFAULT_UNIT
    current_size = size_human_to_float(actual_data[Preferences.KEY_SIZE], size_unit)
    acceptable_size_lo = size_human_to_float(preferences.acceptable_size_range[0], size_unit)
    acceptable_size_hi = size_human_to_float(preferences.acceptable_size_range[1], size_unit)
    matcher.acceptable_size_matched = acceptable_size_lo < current_size < acceptable_size_hi

    return matcher
