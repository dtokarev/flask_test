import re
from collections import OrderedDict


def generate_keywords(*keys: str, year=None):
    def get_year_str():
        return str(year) if year else ''

    result = list()
    keys = [k.strip() for k in keys if k]

    clean_keys = [re.sub(r"\([^)]*\)", '', key).strip() for key in keys]
    result.append( '{} {}'.format(' '.join(keys), get_year_str()) )
    result.append( '{} {}'.format(' '.join(clean_keys), get_year_str()) )
    # result.append( '{}'.format(keys[0]) )
    result.append( '{} {}'.format(clean_keys[0], get_year_str()) )
    result.append(' '.join(clean_keys))

    # strip if stripped version is not empty
    result = [i.strip() for i in result if i.strip()]

    # ordered unique list
    result = list(OrderedDict.fromkeys(result))

    return result
