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


# def html_to_text(html: str) -> str:
#     html = re.sub(r'<br[^>]*>\s*', '\n', html)      # br to \n
#     html = re.sub(r'</p>\s*', '\n', html)           # closing p tag to \n
#
#     bs = BeautifulSoup(html, 'html.parser')
#     [x.extract() for x in bs.findAll('script')]
#     [x.extract() for x in bs.findAll('style')]
#
#     text = bs.get_text()
#
#     text = text.replace('\xa0', ' ')
#     text = re.sub(r'\s\s+', ' ', text)           # whitespaces
#     text = re.sub(r'\n\n+', '\n', text)           # newlines
#
#     return text.strip()
