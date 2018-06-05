import re

KB = 'KB'
MB = 'MB'
GB = 'GB'

units_in_bytes = {
    'KB': 1024,
    'MB': 1024**2,
    'GB': 1024**3,
}


def size_human_to_float(size_str: str, out_unit: str= 'KB') -> float:
    """
    parses string '10 GB' to number in specified units
    :param size_str:
    :param out_unit:
    :return:
    """
    size_str = size_str.replace('\n', ' ')
    data = re.search("([0-9.]+)\s*(KB|MB|GB)", size_str, re.IGNORECASE)

    if not data \
            or len(data.groups()) != 2 \
            or data.group(2).upper() not in units_in_bytes \
            or out_unit.upper() not in units_in_bytes:
        raise ValueError("could not parse size {}".format(size_str))

    size = float(data.group(1))
    unit = data.group(2).upper()

    in_bytes = int(size * units_in_bytes[unit])

    return round(in_bytes / units_in_bytes[out_unit.upper()], 2)
