import re


def generate_keyword_set(keyword: str, year=''):
    result = set()
    result.add('{} {}'.format(keyword, year))

    # removing all parentheses
    result.add( re.sub(r"\([^)]*\)", '', '{} {}'.format(keyword, year)) )
    result.add(keyword)

    return result
