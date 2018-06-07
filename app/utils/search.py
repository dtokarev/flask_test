import re
from collections import OrderedDict


def generate_keywords(keyword: str, year=''):
    # result needs to be ordered set
    result = list()
    clean_keyword = re.sub(r"\([^)]*\)", '', keyword).strip()

    result.append('{} {}'.format(keyword, year).strip())
    # result.append(keyword)
    result.append('{} {}'.format(clean_keyword, year).strip())

    return list(OrderedDict.fromkeys(result))
