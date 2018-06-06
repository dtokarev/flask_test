import re

KB = 'KB'
MB = 'MB'
GB = 'GB'

units_in_bytes = {
    'KB': 1024,
    'MB': 1024**2,
    'GB': 1024**3,
}


def size_human_to_float(human_str: str, out_unit: str='KB', precision: int=2) -> float:
    """
    parses string '10 GB' to number in specified units
    :param precision:
    :param human_str:
    :param out_unit:
    :return:
    """
    human_str = human_str.replace('\n', ' ')
    data = re.search(r"([0-9.]+)\s*(KB|MB|GB)", human_str, re.IGNORECASE)

    if not data \
            or len(data.groups()) != 2 \
            or data.group(2).upper() not in units_in_bytes \
            or out_unit.upper() not in units_in_bytes:
        raise ValueError("could not parse size {}".format(human_str))

    size = float(data.group(1))
    unit = data.group(2).upper()

    in_bytes = int(size * units_in_bytes[unit])

    return round(in_bytes / units_in_bytes[out_unit.upper()], precision)


def duration_human_to_sec(human_str: str):
    try:
        h, m, s = tuple(int(v.strip()) for v in human_str.split(':'))
        return h*3600 + m*60 + s
    except:
        return None
