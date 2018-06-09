import re
from collections import OrderedDict


def generate_keywords(*keys: str, year=''):
    result = list()
    keys = [k.strip() for k in keys if k.strip()]

    clean_keys = [re.sub(r"\([^)]*\)", '', key).strip() for key in keys]

    result.append(' '.join(keys) + ' {}'.format(year))
    result.append(' '.join(clean_keys) + ' {}'.format(year))
    result.append(keys[0] + ' {}'.format(year))
    result.append(clean_keys[0] + ' {}'.format(year))
    result.append(' '.join(keys))

    # strip if stripped version is not empty
    result = [i.strip() for i in result if i.strip()]

    # ordered unique list
    result = list(OrderedDict.fromkeys(result))

    return result