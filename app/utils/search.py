import re
from collections import OrderedDict

from bs4 import BeautifulSoup


def generate_keywords(keyword: str, year=''):
    # result needs to be ordered set
    result = list()
    clean_keyword = re.sub(r"\([^)]*\)", '', keyword).strip()

    result.append('{} {}'.format(keyword, year).strip())
    result.append(keyword)
    result.append(clean_keyword)

    return list(OrderedDict.fromkeys(result))
